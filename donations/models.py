
from django.conf import settings
from django.db import models
from django.utils import timezone


class FoodDonation(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("collected", "Collected"),
        ("delivered", "Delivered"),
    ]

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="food_donations",
    )
    food_name = models.CharField(max_length=150)
    description = models.TextField()
    quantity = models.PositiveIntegerField(
        help_text="Quantity in servings"
    )
    pickup_location = models.CharField(max_length=255)
    safe_until = models.DateTimeField(
        help_text="Latest safe-consumption date and time"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default="available",
    )

    def __str__(self):
        return self.food_name

    @property
    def is_still_safe(self):
        return self.safe_until > timezone.now()


class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("collected", "Collected"),
        ("delivered", "Delivered"),
    ]

    food = models.ForeignKey(
        FoodDonation,
        on_delete=models.CASCADE,
        related_name="requests",
    )
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donation_requests",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["food", "ngo"],
                name="unique_food_request_per_ngo",
            )
        ]

    def __str__(self):
        return f"{self.ngo.username} - {self.food.food_name}"
