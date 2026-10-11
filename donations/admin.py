
from django.contrib import admin
from .models import FoodDonation, DonationRequest


@admin.register(FoodDonation)
class FoodDonationAdmin(admin.ModelAdmin):
    list_display = (
        "food_name", "donor", "quantity", "status", "safe_until"
    )
    list_filter = ("status",)
    search_fields = ("food_name", "pickup_location", "donor__username")


@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ("food", "ngo", "status", "requested_at")
    list_filter = ("status",)
