
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from .models import FoodDonation


class FoodDonationTests(TestCase):
    def test_donor_can_create_food_donation(self):
        donor = User.objects.create_user(
            username="donor1",
            password="TestPassword123!",
            role="donor",
        )
        food = FoodDonation.objects.create(
            donor=donor,
            food_name="Vegetable meals",
            description="Freshly prepared meals",
            quantity=20,
            pickup_location="Community Hall",
            safe_until=timezone.now() + timedelta(hours=4),
        )
        self.assertEqual(food.status, "available")
        self.assertEqual(food.quantity, 20)
