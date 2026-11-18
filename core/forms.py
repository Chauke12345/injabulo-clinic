from django import forms
from django.utils import timezone
from .models import HomepageContent, Appointment


class HomepageContentForm(forms.ModelForm):
    class Meta:
        model = HomepageContent
        exclude = ["updated_at"]

        widgets = {
            "hero_description": forms.Textarea(attrs={"rows": 3}),
            "about_paragraph_1": forms.Textarea(attrs={"rows": 4}),
            "about_paragraph_2": forms.Textarea(attrs={"rows": 4}),
            "mission_text": forms.Textarea(attrs={"rows": 4}),
            "vision_text": forms.Textarea(attrs={"rows": 4}),
        }

class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = [
            "patient_name",
            "contact_number",
            "service",
            "preferred_date",
            "preferred_time",
            "booking_message",
        ]

        labels = {
            "patient_name": "Full name",
            "contact_number": "Contact number",
            "service": "Healthcare service",
            "preferred_date": "Preferred appointment date",
            "preferred_time": "Preferred appointment time",
            "booking_message": "Additional booking information (optional)",
        }

        widgets = {
            "patient_name": forms.TextInput(attrs={
                "placeholder": "Enter your full name",
                "autocomplete": "name",
            }),
            "contact_number": forms.TextInput(attrs={
                "placeholder": "e.g. 071 234 5678",
                "type": "tel",
                "autocomplete": "tel",
            }),
            "service": forms.Select(),
            "preferred_date": forms.DateInput(attrs={
                "type": "date",
            }),
            "preferred_time": forms.TimeInput(attrs={
                "type": "time",
            }),
            "booking_message": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Optional information about your booking. Please do not include medical history or diagnoses.",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = (
            self.fields["service"].queryset.filter(is_active=True)
        )

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]

        if preferred_date < timezone.localdate():
            raise forms.ValidationError(
                "Please select today or a future date."
            )

        return preferred_date

    def clean_patient_name(self):
        return self.cleaned_data["patient_name"].strip()

    def clean_contact_number(self):
        return self.cleaned_data["contact_number"].strip()

