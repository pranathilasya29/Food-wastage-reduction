
from django.contrib import admin
from .models import DeliveryTracking


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "donation_request",
        "status",
        "collected_at",
        "delivered_at",
    )
    list_filter = ("status",)
