from django.contrib import admin
from .models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "event_date",
        "is_published",
        "display_order",
    )

    list_filter = ("category", "is_published", "event_date")
    search_fields = ("title", "caption")
    list_editable = ("is_published", "display_order")
    ordering = ("display_order", "-created_at")
