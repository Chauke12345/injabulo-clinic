from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "event_date",
        "is_published",
        "display_order",
    )

    list_filter = ("category", "is_published", "event_date")
    search_fields = ("title", "short_description", "description")
    list_editable = ("is_published", "display_order")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-event_date", "display_order")
