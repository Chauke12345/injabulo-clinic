from django.db import models


class Video(models.Model):
    CATEGORY_CHOICES = [
        ("womens_health", "Women's Health"),
        ("pregnancy", "Pregnancy & Maternal Care"),
        ("child_health", "Child Health"),
        ("general_health", "General Health Education"),
        ("preventative", "Preventative Healthcare"),
        ("beauty_wellness", "Beauty & Wellness"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="general_health",
    )
    video_file = models.FileField(upload_to="health_videos/")
    thumbnail = models.ImageField(
        upload_to="health_video_thumbnails/",
        blank=True,
        null=True,
    )
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
