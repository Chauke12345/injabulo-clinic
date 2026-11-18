from pathlib import Path

path = Path("core/models.py")
content = path.read_text(encoding="utf-8")

if "class Appointment(models.Model):" in content:
    raise SystemExit("STOP: Appointment model already exists.")

if "from services.models import Service" not in content:
    content = content.replace(
        "from django.db import models",
        "from django.db import models\nfrom services.models import Service",
        1,
    )

appointment_model = '''

class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        RESCHEDULED = "rescheduled", "Rescheduled"
        DECLINED = "declined", "Declined"

    patient_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20)

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointment_requests",
    )

    preferred_date = models.DateField()
    preferred_time = models.TimeField(
        blank=True,
        null=True,
    )

    booking_message = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional booking information. Do not include medical history or diagnoses.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    confirmed_date = models.DateField(
        blank=True,
        null=True,
    )
    confirmed_time = models.TimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Appointment Request"
        verbose_name_plural = "Appointment Requests"

    def __str__(self):
        return f"{self.patient_name} - {self.service.title} ({self.get_status_display()})"
'''

content = content.rstrip() + appointment_model + "\n"
path.write_text(content, encoding="utf-8")

print("SUCCESS: Appointment model added.")
