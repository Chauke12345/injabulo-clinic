from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = [
            "display_name",
            "testimonial",
            "rating",
            "consent_to_publish",
            "is_approved",
            "is_featured",
        ]

class PublicTestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = [
            "display_name",
            "testimonial",
            "rating",
            "consent_to_publish",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={
                "placeholder": "Your name (optional)"
            }),
            "testimonial": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Share your experience with Injabulo Clinic..."
            }),
            "rating": forms.Select(),
            "consent_to_publish": forms.CheckboxInput(),
        }

    def clean_consent_to_publish(self):
        consent = self.cleaned_data.get("consent_to_publish")
        if not consent:
            raise forms.ValidationError(
                "Please give permission for your review to be published."
            )
        return consent
