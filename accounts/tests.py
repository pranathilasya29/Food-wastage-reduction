
from django.test import TestCase
from .models import User


class UserModelTests(TestCase):
    def test_donor_role(self):
        user = User.objects.create_user(
            username="testdonor",
            password="TestPassword123!",
            role="donor",
        )
        self.assertEqual(user.role, "donor")
