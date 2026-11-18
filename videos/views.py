from django.shortcuts import render
from .models import Video


def video_library(request):
    videos = Video.objects.filter(is_published=True)
    categories = Video.CATEGORY_CHOICES

    selected_category = request.GET.get("category", "")
    if selected_category:
        videos = videos.filter(category=selected_category)

    return render(request, "videos/video_library.html", {
        "videos": videos,
        "categories": categories,
        "selected_category": selected_category,
    })
