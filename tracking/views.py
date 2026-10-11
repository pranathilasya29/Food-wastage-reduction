
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from donations.models import DonationRequest, FoodDonation
from .models import DeliveryTracking


@login_required
def track_donation(request, pk):
    donation_request = get_object_or_404(
        DonationRequest.objects.select_related("food", "ngo", "food__donor"),
        pk=pk,
    )

    if request.user.pk not in (
        donation_request.ngo_id,
        donation_request.food.donor_id,
    ):
        messages.error(request, "You cannot view this donation's tracking.")
        return redirect("dashboard")

    tracking = DeliveryTracking.objects.filter(
        donation_request=donation_request
    ).first()

    return render(
        request,
        "tracking/track_donation.html",
        {
            "donation_request": donation_request,
            "tracking": tracking,
        },
    )


@login_required
@require_POST
def update_tracking(request, pk):
    if request.user.role != "ngo":
        messages.error(request, "Only the requesting NGO can update tracking.")
        return redirect("dashboard")

    donation_request = get_object_or_404(
        DonationRequest.objects.select_related("food"),
        pk=pk,
        ngo=request.user,
    )

    tracking = get_object_or_404(
        DeliveryTracking,
        donation_request=donation_request,
    )

    new_status = request.POST.get("status")
    allowed_transitions = {
        "approved": ["collected"],
        "collected": ["delivered"],
    }

    if new_status not in allowed_transitions.get(tracking.status, []):
        messages.error(request, "Invalid tracking status transition.")
        return redirect("track_donation", pk=pk)

    tracking.update_status(new_status)
    donation_request.status = new_status
    donation_request.save(update_fields=["status"])

    food = donation_request.food
    food.status = new_status
    food.save(update_fields=["status"])

    messages.success(request, "Donation tracking updated.")
    return redirect("track_donation", pk=pk)
