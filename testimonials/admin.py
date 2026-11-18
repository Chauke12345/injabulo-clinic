from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("display_name", "rating", "is_approved", "is_featured", "consent_to_publish", "created_at")
    list_filter = ("is_approved", "is_featured", "consent_to_publish", "rating")
    search_fields = ("display_name", "testimonial")
