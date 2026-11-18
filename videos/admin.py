from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_published",
        "is_featured",
        "created_at",
    )
    list_filter = ("category", "is_published", "is_featured")
    search_fields = ("title", "description")
    list_editable = ("is_published", "is_featured")
    ordering = ("-created_at",)
