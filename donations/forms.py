
from django import forms
from django.utils import timezone
from .models import FoodDonation


class FoodDonationForm(forms.ModelForm):
    safe_until = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = FoodDonation
        fields = [
            "food_name",
            "description",
            "quantity",
            "pickup_location",
            "safe_until",
        ]

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_safe_until(self):
        safe_until = self.cleaned_data["safe_until"]
        if timezone.is_naive(safe_until):
            safe_until = timezone.make_aware(
                safe_until, timezone.get_current_timezone()
            )
        if safe_until <= timezone.now():
            raise forms.ValidationError(
                "Choose a future safe-consumption deadline."
            )
        return safe_until
