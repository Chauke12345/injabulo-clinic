from django.shortcuts import render
from .models import GalleryImage


def gallery_list(request):
    images = GalleryImage.objects.filter(
        is_published=True
    )

    return render(request, "gallery/gallery_list.html", {
        "images": images
    })
