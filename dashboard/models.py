from django.db import models


class DashboardNotification(models.Model):
    appointment = models.OneToOneField(
        "core.Appointment",
        on_delete=models.CASCADE,
        related_name="dashboard_notification",
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Dashboard Notification"
        verbose_name_plural = "Dashboard Notifications"

    def __str__(self):
        return f"Notification for appointment #{self.appointment_id}"
