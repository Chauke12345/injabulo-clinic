from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Testimonial(models.Model):
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional. Leave blank to publish anonymously."
    )
    testimonial = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    consent_to_publish = models.BooleanField(
        default=False,
        help_text="Confirm that the patient has agreed to publication."
    )
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or "Anonymous testimonial"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient Testimonial"
        verbose_name_plural = "Patient Testimonials"
