from pathlib import Path

path = Path("core/forms.py")
content = path.read_text(encoding="utf-8")

if "class AppointmentForm" in content:
    raise SystemExit("STOP: AppointmentForm already exists.")

content = content.replace(
    "from django import forms",
    "from django import forms\nfrom django.utils import timezone",
    1,
)

content = content.replace(
    "from .models import HomepageContent",
    "from .models import HomepageContent, Appointment",
    1,
)

appointment_form = '''

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
'''

path.write_text(content.rstrip() + appointment_form + "\n", encoding="utf-8")

print("SUCCESS: AppointmentForm added.")
