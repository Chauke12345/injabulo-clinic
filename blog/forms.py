from django import forms
from .models import BlogCategory, BlogPost


class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ["name"]


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            "category", "title", "excerpt", "content",
            "featured_image", "author", "is_published",
            "is_featured", "published_at"
        ]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 12}),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
