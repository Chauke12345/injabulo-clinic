from django.db import models
from services.models import Service

# Create your models here.

class HomepageContent(models.Model):
    # HERO SECTION
    hero_label = models.CharField(
        max_length=100,
        default="WELCOME TO INJABULO CLINIC"
    )
    hero_heading_line_1 = models.CharField(
        max_length=100,
        default="Your Health,"
    )
    hero_heading_line_2 = models.CharField(
        max_length=100,
        default="Your Beauty,"
    )
    hero_heading_line_3 = models.CharField(
        max_length=100,
        default="Our Care."
    )
    hero_description = models.TextField(
        default=(
            "Compassionate healthcare and personalised attention "
            "for you and your family's wellbeing."
        )
    )

    # ABOUT SECTION
    about_label = models.CharField(
        max_length=100,
        default="GET TO KNOW US"
    )
    about_heading = models.CharField(
        max_length=200,
        default="Healthcare with a human touch."
    )
    about_paragraph_1 = models.TextField(
        default=(
            "Injabulo Clinic is a healthcare practice dedicated to "
            "providing compassionate, professional and patient-centred "
            "nursing care. We believe that every individual deserves "
            "to be treated with dignity, respect and understanding."
        )
    )
    about_paragraph_2 = models.TextField(
        default=(
            "Led by Sr H.G. Fankomo, Professional Nurse, Injabulo Clinic "
            "is committed to supporting individuals, families and "
            "communities through accessible healthcare services, "
            "health education and wellness initiatives."
        )
    )
    nurse_name = models.CharField(
        max_length=150,
        default="Sr H.G. Fankomo"
    )
    nurse_title = models.CharField(
        max_length=150,
        default="Professional Nurse"
    )

    # MISSION, VISION AND VALUES
    mission_heading = models.CharField(
        max_length=150,
        default="Our Mission"
    )
    mission_text = models.TextField(
        default=(
            "To provide compassionate, professional and accessible "
            "healthcare services that promote health, prevent illness "
            "and improve the wellbeing of individuals, families and communities."
        )
    )
    vision_heading = models.CharField(
        max_length=150,
        default="Our Vision"
    )
    vision_text = models.TextField(
        default=(
            "To become a trusted healthcare provider recognised for quality "
            "nursing care, compassion, professionalism and a meaningful "
            "contribution to healthier communities."
        )
    )

    value_1_heading = models.CharField(max_length=100, default="Compassion")
    value_1_description = models.CharField(
        max_length=250,
        default="Treating every patient with kindness."
    )
    value_2_heading = models.CharField(max_length=100, default="Integrity")
    value_2_description = models.CharField(
        max_length=250,
        default="Maintaining honesty and professional standards."
    )
    value_3_heading = models.CharField(max_length=100, default="Respect")
    value_3_description = models.CharField(
        max_length=250,
        default="Respecting every individual."
    )
    value_4_heading = models.CharField(max_length=100, default="Professionalism")
    value_4_description = models.CharField(
        max_length=250,
        default="Striving for responsible, quality care."
    )

    # SERVICES INTRODUCTION
    services_label = models.CharField(
        max_length=100,
        default="HOW WE CAN HELP"
    )
    services_heading = models.CharField(
        max_length=200,
        default="Our Healthcare Services"
    )
    services_description = models.CharField(
        max_length=300,
        default=(
            "Thoughtful healthcare services designed around your "
            "health and wellbeing."
        )
    )

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError(
            "The homepage content record cannot be deleted."
        )

    def __str__(self):
        return "Injabulo Clinic Homepage Content"

    class Meta:
        verbose_name = "Homepage Content"
        verbose_name_plural = "Homepage Content"

class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        RESCHEDULED = "rescheduled", "Rescheduled"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"

    class CommunicationStatus(models.TextChoices):
        NOT_CONTACTED = "not_contacted", "Not Contacted"
        CONTACTED = "contacted", "Contacted"

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

    communication_status = models.CharField(
        max_length=20,
        choices=CommunicationStatus.choices,
        default=CommunicationStatus.NOT_CONTACTED,
    )

    contacted_at = models.DateTimeField(
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


