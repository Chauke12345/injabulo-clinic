from django import forms
from PIL import Image, UnidentifiedImageError

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "category",
            "short_description",
            "description",
            "event_date",
            "event_time",
            "location",
            "image",
            "is_published",
            "display_order",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Enter event title",
            }),
            "category": forms.Select(),
            "short_description": forms.TextInput(attrs={
                "placeholder": "A short summary of this event",
            }),
            "description": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": "Enter the full event description",
            }),
            "event_date": forms.DateInput(attrs={
                "type": "date",
            }),
            "event_time": forms.TimeInput(attrs={
                "type": "time",
            }),
            "location": forms.TextInput(attrs={
                "placeholder": "Enter event venue or location",
            }),
            "image": forms.ClearableFileInput(attrs={
                "accept": "image/*",
            }),
            "is_published": forms.CheckboxInput(),
            "display_order": forms.NumberInput(attrs={
                "min": 0,
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if image and hasattr(image, "content_type"):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image size must not exceed 5 MB."
                )

            try:
                image.seek(0)
                with Image.open(image) as uploaded_image:
                    uploaded_image.verify()
                image.seek(0)
            except (UnidentifiedImageError, OSError, ValueError):
                raise forms.ValidationError(
                    "Please upload a valid image file."
                )

        return image
