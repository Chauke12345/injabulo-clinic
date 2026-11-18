from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("display_order", "title")
