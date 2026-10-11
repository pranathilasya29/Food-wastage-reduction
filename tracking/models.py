
from django.db import models
from django.utils import timezone


class DeliveryTracking(models.Model):
    STATUS_CHOICES = [
        ("approved", "Approved"),
        ("collected", "Collected"),
        ("delivered", "Delivered"),
    ]

    donation_request = models.OneToOneField(
        "donations.DonationRequest",
        on_delete=models.CASCADE,
        related_name="tracking",
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default="approved",
    )
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking #{self.pk} - {self.status}"

    def update_status(self, new_status):
        self.status = new_status

        if new_status == "collected" and not self.collected_at:
            self.collected_at = timezone.now()

        if new_status == "delivered" and not self.delivered_at:
            self.delivered_at = timezone.now()

        self.save()
