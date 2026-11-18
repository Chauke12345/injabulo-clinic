from django.db import models


class TeamMember(models.Model):
    full_name = models.CharField(max_length=150)
    job_title = models.CharField(max_length=150)
    qualifications = models.CharField(max_length=255, blank=True)
    biography = models.TextField(blank=True)
    photograph = models.ImageField(
        upload_to="team/",
        blank=True,
        null=True
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job_title}"

    class Meta:
        ordering = ["display_order", "full_name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
