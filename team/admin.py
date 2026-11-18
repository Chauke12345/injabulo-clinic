from django.contrib import admin
from .models import TeamMember

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "job_title", "display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("full_name", "job_title", "qualifications")
