from django import forms
from .models import GalleryImage


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = [
            "title",
            "image",
            "category",
            "caption",
            "event_date",
            "is_published",
            "display_order",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Enter image title",
            }),
            "image": forms.ClearableFileInput(attrs={
                "accept": "image/*",
            }),
            "category": forms.Select(),
            "caption": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Enter an optional image caption",
            }),
            "event_date": forms.DateInput(attrs={
                "type": "date",
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

            from PIL import Image, UnidentifiedImageError

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
