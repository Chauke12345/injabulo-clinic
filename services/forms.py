from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "title",
            "short_description",
            "description",
            "is_active",
            "show_on_homepage",
            "display_order",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Women's Healthcare",
            }),
            "short_description": forms.TextInput(attrs={
                "placeholder": "A short description of this service",
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Enter the full service description",
            }),
            "is_active": forms.CheckboxInput(),
            "show_on_homepage": forms.CheckboxInput(),
            "display_order": forms.NumberInput(attrs={
                "min": 0,
            }),
        }
