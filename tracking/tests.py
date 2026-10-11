
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from donations.models import FoodDonation, DonationRequest
from .models import DeliveryTracking


class DeliveryTrackingTests(TestCase):
    def test_tracking_starts_as_approved(self):
        donor = User.objects.create_user(
            username="donor",
            password="TestPassword123!",
            role="donor",
        )
        ngo = User.objects.create_user(
            username="ngo",
            password="TestPassword123!",
            role="ngo",
        )
        food = FoodDonation.objects.create(
            donor=donor,
            food_name="Rice meals",
            description="Prepared meals",
            quantity=10,
            pickup_location="Community Hall",
            safe_until=timezone.now() + timedelta(hours=4),
            status="approved",
        )
        donation_request = DonationRequest.objects.create(
            food=food,
            ngo=ngo,
            status="approved",
        )
        tracking = DeliveryTracking.objects.create(
            donation_request=donation_request,
        )

        self.assertEqual(tracking.status, "approved")
