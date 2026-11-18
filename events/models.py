from django.db import models


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("awareness", "Health Awareness"),
        ("outreach", "Community Outreach"),
        ("corporate", "Corporate Wellness"),
        ("clinic", "Clinic Events"),
        ("announcement", "Clinic Announcements"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="clinic"
    )
    short_description = models.CharField(max_length=250)
    description = models.TextField()
    event_date = models.DateField(null=True, blank=True)
    event_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-event_date", "display_order"]
        verbose_name = "Clinic Event"
        verbose_name_plural = "Clinic Events"
