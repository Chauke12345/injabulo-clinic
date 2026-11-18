from django.db import models


class CorporateEnquiry(models.Model):
    SERVICE_CHOICES = [
        ("workplace_screening", "Workplace Health Screening"),
        ("employee_assessments", "Employee Medical Assessments"),
        ("corporate_wellness", "Corporate Wellness Programme"),
        ("onsite_nursing", "On-site Nursing Services"),
        ("wellness_campaign", "Workplace Wellness Campaign"),
        ("other", "Other Corporate Healthcare Services"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("quoted", "Quotation Sent"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=150, blank=True)
    contact_person = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    employee_count = models.PositiveIntegerField()
    service_type = models.CharField(max_length=40, choices=SERVICE_CHOICES)
    preferred_date = models.DateField(blank=True, null=True)
    service_location = models.CharField(max_length=255)
    additional_requirements = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )
    staff_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Corporate Wellness Enquiry"
        verbose_name_plural = "Corporate Wellness Enquiries"

    def __str__(self):
        return f"{self.company_name} - {self.get_service_type_display()}"


class CorporateQuotation(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    enquiry = models.ForeignKey(
        CorporateEnquiry,
        on_delete=models.PROTECT,
        related_name="quotations",
    )
    reference = models.CharField(max_length=30, unique=True)
    issue_date = models.DateField()
    valid_until = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.enquiry.company_name}"


class CorporateQuotationItem(models.Model):
    quotation = models.ForeignKey(
        CorporateQuotation,
        on_delete=models.CASCADE,
        related_name="items",
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description
