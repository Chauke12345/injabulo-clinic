from django.db import models


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ("clinic", "Our Clinic"),
        ("team", "Our Healthcare Team"),
        ("community", "Community Outreach"),
        ("awareness", "Health Awareness Events"),
        ("corporate", "Corporate Wellness"),
    ]

    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to="gallery/")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="clinic"
    )
    caption = models.CharField(max_length=250, blank=True)
    event_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return self.title
