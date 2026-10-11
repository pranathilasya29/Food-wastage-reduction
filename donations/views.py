
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import FoodDonationForm
from .models import FoodDonation, DonationRequest


def home(request):
    available_foods = FoodDonation.objects.filter(
        status="available",
        safe_until__gt=timezone.now(),
    ).order_by("-created_at")[:6]

    return render(
        request,
        "home.html",
        {"available_foods": available_foods},
    )


@login_required
def dashboard(request):
    if request.user.role == "donor":
        donations = FoodDonation.objects.filter(
            donor=request.user
        ).order_by("-created_at")
        return render(
            request,
            "dashboard.html",
            {"donations": donations},
        )

    requests = DonationRequest.objects.filter(
        ngo=request.user
    ).select_related("food").order_by("-requested_at")

    return render(
        request,
        "dashboard.html",
        {"requests": requests},
    )


def food_list(request):
    foods = FoodDonation.objects.filter(
        status="available",
        safe_until__gt=timezone.now(),
    ).select_related("donor").order_by("-created_at")

    return render(request, "donations/food_list.html", {"foods": foods})


def food_detail(request, pk):
    food = get_object_or_404(FoodDonation, pk=pk)
    return render(request, "donations/food_detail.html", {"food": food})


@login_required
def add_food(request):
    if request.user.role != "donor":
        messages.error(request, "Only donors can list food.")
        return redirect("food_list")

    form = FoodDonationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        food = form.save(commit=False)
        food.donor = request.user
        food.save()
        messages.success(request, "Food donation listed successfully.")
        return redirect("my_donations")

    return render(request, "donations/add_food.html", {"form": form})


@login_required
def my_donations(request):
    foods = FoodDonation.objects.filter(
        donor=request.user
    ).order_by("-created_at")

    return render(request, "donations/my_donations.html", {"foods": foods})


@login_required
@require_POST
def request_food(request, pk):
    if request.user.role != "ngo":
        messages.error(request, "Only registered NGOs can request food.")
        return redirect("food_list")

    with transaction.atomic():
        food = get_object_or_404(
            FoodDonation.objects.select_for_update(),
            pk=pk,
        )

        if food.donor_id == request.user.id:
            messages.error(request, "You cannot request your own donation.")
        elif food.status != "available" or food.safe_until <= timezone.now():
            messages.error(request, "This food is no longer available.")
        else:
            _, created = DonationRequest.objects.get_or_create(
                food=food,
                ngo=request.user,
            )
            if created:
                food.status = "requested"
                food.save(update_fields=["status"])
                messages.success(request, "Your request has been submitted.")
            else:
                messages.info(request, "You have already requested this food.")

    return redirect("food_detail", pk=pk)


@login_required
def request_list(request):
    if request.user.role == "ngo":
        requests = DonationRequest.objects.filter(
            ngo=request.user
        ).select_related("food", "food__donor")
    else:
        requests = DonationRequest.objects.filter(
            food__donor=request.user
        ).select_related("food", "ngo")

    return render(
        request,
        "donations/request_list.html",
        {"requests": requests},
    )


@login_required
@require_POST
def approve_request(request, pk):
    if request.user.role != "donor":
        messages.error(request, "Only donors can approve requests.")
        return redirect("request_list")

    with transaction.atomic():
        donation_request = get_object_or_404(
            DonationRequest.objects.select_for_update().select_related("food"),
            pk=pk,
            food__donor=request.user,
        )
        food = donation_request.food

        if donation_request.status != "pending" or food.status != "requested":
            messages.error(request, "This request cannot be approved.")
        elif food.safe_until <= timezone.now():
            messages.error(request, "The food's safe-consumption deadline has passed.")
        else:
            donation_request.status = "approved"
            donation_request.save(update_fields=["status"])
            food.status = "approved"
            food.save(update_fields=["status"])

            from tracking.models import DeliveryTracking
            DeliveryTracking.objects.get_or_create(
                donation_request=donation_request
            )
            messages.success(request, "Request approved.")

    return redirect("request_list")


@login_required
@require_POST
def reject_request(request, pk):
    if request.user.role != "donor":
        messages.error(request, "Only donors can reject requests.")
        return redirect("request_list")

    with transaction.atomic():
        donation_request = get_object_or_404(
            DonationRequest.objects.select_for_update().select_related("food"),
            pk=pk,
            food__donor=request.user,
        )

        if donation_request.status != "pending":
            messages.error(request, "This request is no longer pending.")
        else:
            food = donation_request.food
            donation_request.status = "rejected"
            donation_request.save(update_fields=["status"])

            # Make food available again only if no other pending
            # request exists for the same donation.
            if not food.requests.filter(status="pending").exists():
                if food.safe_until > timezone.now():
                    food.status = "available"
                else:
                    food.status = "delivered"  # unavailable; deadline passed
                food.save(update_fields=["status"])

            messages.success(request, "Request rejected.")

    return redirect("request_list")
