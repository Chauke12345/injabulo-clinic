from django.contrib import messages
from django.shortcuts import render, redirect
from .models import HomepageContent, Appointment
from .forms import AppointmentForm
from videos.models import Video
from gallery.models import GalleryImage
from blog.models import BlogPost
from team.models import TeamMember
from services.models import Service
from events.models import Event
from django.utils import timezone


def home(request):
    upcoming_event = Event.objects.filter(
        is_published=True,
        event_date__gte=timezone.localdate()
    ).order_by("event_date", "event_time", "display_order").first()

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
        "upcoming_event": upcoming_event,
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

            from dashboard.models import DashboardNotification

            DashboardNotification.objects.create(
                appointment=appointment_request,
                message=(
                    f"New online appointment booking received "
                    f"(Reference #{appointment_request.pk}). "
                    f"Please log in to the Injabulo Clinic dashboard to view and manage it."
                ),
            )

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



def booking_app(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment_request = form.save()

            from dashboard.models import DashboardNotification

            DashboardNotification.objects.create(
                appointment=appointment_request,
                message=(
                    f"New Booking App appointment received "
                    f"(Reference #{appointment_request.pk}). "
                    f"Please log in to the Injabulo Clinic dashboard to view and manage it."
                ),
            )

            messages.success(
                request,
                f"Your appointment request was received successfully! "
                f"Your booking reference is #{appointment_request.pk}. "
                f"Thank you for choosing Injabulo Clinic. "
                f"Our team will contact you to confirm your appointment."
            )

            return redirect("booking_app")

    else:
        form = AppointmentForm(
            initial={
                "service": request.GET.get("service")
            }
        )

    return render(request, "core/booking_app.html", {
        "form": form,
    })

def booking_app_preview(request):
    form = AppointmentForm()
    messages.success(
        request,
        "DEMO ONLY — Your sample booking reference is DEMO-001. "
        "No appointment has been saved and no clinic notification has been sent."
    )
    return render(request, "core/booking_app.html", {
        "form": form,
        "preview_mode": True,
    })

from django.http import HttpResponse


def robots_txt(request):
    content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /dashboard/
Disallow: /booking-app/preview/

Sitemap: https://injabulo-clinic-website-production.up.railway.app/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")
