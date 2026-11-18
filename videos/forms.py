from django import forms
from .models import Video


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "title",
            "description",
            "category",
            "video_file",
            "thumbnail",
            "is_published",
            "is_featured",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Enter video title",
            }),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Describe the health education video",
            }),
            "video_file": forms.ClearableFileInput(attrs={
                "accept": ".mp4,.mov,.webm,.m4v,video/mp4,video/quicktime,video/webm",
            }),
            "thumbnail": forms.ClearableFileInput(attrs={
                "accept": "image/*",
            }),
        }

    def clean_video_file(self):
        video = self.cleaned_data.get("video_file")

        if video and hasattr(video, "name"):
            allowed_extensions = (".mp4", ".mov", ".webm", ".m4v")

            if not video.name.lower().endswith(allowed_extensions):
                raise forms.ValidationError(
                    "Upload an MP4, MOV, WebM or M4V video."
                )

            if video.size > 500 * 1024 * 1024:
                raise forms.ValidationError(
                    "Video size must not exceed 500 MB."
                )

        return video

    def clean_thumbnail(self):
        image = self.cleaned_data.get("thumbnail")

        if image and hasattr(image, "content_type"):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Thumbnail size must not exceed 5 MB."
                )

            from PIL import Image, UnidentifiedImageError

            try:
                image.seek(0)
                with Image.open(image) as uploaded_image:
                    uploaded_image.verify()
                image.seek(0)
            except (UnidentifiedImageError, OSError, ValueError):
                raise forms.ValidationError(
                    "Please upload a valid thumbnail image."
                )

        return image
