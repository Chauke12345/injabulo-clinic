from django import forms
from .models import TeamMember


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            "full_name", "job_title", "qualifications",
            "biography", "photograph", "display_order", "is_active"
        ]
        widgets = {
            "biography": forms.Textarea(attrs={"rows": 5}),
        }
