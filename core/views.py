from django.contrib import messages
from django.shortcuts import render, redirect
from .models import HomepageContent, Appointment
from .forms import AppointmentForm
from videos.models import Video
from gallery.models import GalleryImage
from blog.models import BlogPost
from team.models import TeamMember
from services.models import Service


def home(request):
    homepage_content = HomepageContent.objects.filter(pk=1).first()
    homepage_services = Service.objects.filter(is_active=True, show_on_homepage=True)[:6]
    latest_videos = Video.objects.filter(is_published=True)[:3]
    team_members = TeamMember.objects.filter(
        is_active=True
    )[:3]

    latest_blog_posts = BlogPost.objects.filter(
        is_published=True
    ).order_by("-published_at", "-created_at")[:2]

    featured_gallery_images = GalleryImage.objects.filter(
        is_published=True
    ).order_by("display_order", "-created_at")[:8]

    return render(request, "core/home.html", {
        "homepage_content": homepage_content,
        "homepage_services": homepage_services,
        "latest_videos": latest_videos,
        "featured_gallery_images": featured_gallery_images,
        "team_members": team_members,
        "latest_blog_posts": latest_blog_posts,
    })


def contact(request):
    return render(request, "core/contact.html")


def appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment_request = form.save()

            messages.success(
                request,
                f"Your appointment request was received. "
                f"Your reference number is #{appointment_request.pk}. "
                f"The clinic will contact you to confirm availability."
            )

            return redirect("appointment")

    else:
        form = AppointmentForm(
            initial={
                "service": request.GET.get("service")
            }
        )

    return render(request, "core/appointment.html", {
        "form": form,
    })

from django.http import FileResponse
from pathlib import Path


def service_worker(request):
    worker_file = (
        Path(__file__).resolve().parent
        / "static"
        / "core"
        / "pwa"
        / "service-worker.js"
    )

    response = FileResponse(
        open(worker_file, "rb"),
        content_type="application/javascript"
    )
    response["Cache-Control"] = "no-cache"
    response["Service-Worker-Allowed"] = "/"
    return response
