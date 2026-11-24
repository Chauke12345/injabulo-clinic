from django.contrib import messages
from django.contrib.auth.views import LoginView

from blog.models import BlogPost, BlogCategory
from blog.forms import BlogPostForm, BlogCategoryForm
from team.models import TeamMember
from team.forms import TeamMemberForm


from django.http import HttpResponse
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from io import BytesIO

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.views.decorators.http import require_POST

from services.models import Service
from services.forms import ServiceForm
from gallery.models import GalleryImage
from gallery.forms import GalleryImageForm
from events.models import Event
from events.forms import EventForm

from core.models import HomepageContent
from .models import DashboardNotification
from core.forms import HomepageContentForm

from videos.models import Video
from videos.forms import VideoForm
from corporate.models import CorporateEnquiry, CorporateQuotation, CorporateQuotationItem
from corporate.forms import CorporateQuotationForm, CorporateQuotationItemForm


class RoleBasedLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_superuser:
            return "/admin/"
        return "/dashboard/"


def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="/dashboard/login/",
    )(view_func)


@staff_required
def dashboard_home(request):
    unread_notifications = DashboardNotification.objects.filter(is_read=False)
    recent_notifications = DashboardNotification.objects.select_related(
        "appointment",
        "appointment__service",
    )[:5]

    context = {
        "total_services": Service.objects.count(),
        "total_gallery": GalleryImage.objects.count(),
        "total_events": Event.objects.filter(is_published=True).count(),
        "unread_notification_count": unread_notifications.count(),
        "recent_notifications": recent_notifications,
    }
    return render(request, "dashboard/home.html", context)


@staff_required
def service_list(request):
    services = Service.objects.all()
    return render(request, "dashboard/services/list.html", {
        "services": services,
    })


@staff_required
def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'"{service.title}" was added successfully.')
            return redirect("dashboard:service_list")
    else:
        form = ServiceForm()

    return render(request, "dashboard/services/form.html", {
        "form": form,
        "page_title": "Add Clinic Service",
        "button_label": "Save Service",
    })


@staff_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'"{service.title}" was updated successfully.')
            return redirect("dashboard:service_list")
    else:
        form = ServiceForm(instance=service)

    return render(request, "dashboard/services/form.html", {
        "form": form,
        "page_title": "Edit Clinic Service",
        "button_label": "Save Changes",
        "service": service,
    })


@staff_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == "POST":
        title = service.title
        service.delete()
        messages.success(request, f'"{title}" was deleted.')
        return redirect("dashboard:service_list")

    return render(request, "dashboard/services/confirm_delete.html", {
        "service": service,
    })


# --------------------------------------------------
# GALLERY MANAGEMENT
# --------------------------------------------------

def _delete_gallery_file_if_unused(storage, file_name):
    if file_name and not GalleryImage.objects.filter(
        image=file_name
    ).exists():
        storage.delete(file_name)


@staff_required
def gallery_list(request):
    images = GalleryImage.objects.all()
    return render(request, "dashboard/gallery/list.html", {
        "images": images,
    })


@staff_required
def gallery_create(request):
    if request.method == "POST":
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            messages.success(
                request,
                f'"{image.title}" was uploaded successfully.'
            )
            return redirect("dashboard:gallery_list")
    else:
        form = GalleryImageForm()

    return render(request, "dashboard/gallery/form.html", {
        "form": form,
        "page_title": "Upload Gallery Image",
        "button_label": "Upload Image",
    })


@staff_required
def gallery_edit(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    old_file_name = image.image.name if image.image else None
    old_storage = image.image.storage if image.image else None

    if request.method == "POST":
        form = GalleryImageForm(
            request.POST,
            request.FILES,
            instance=image,
        )

        if form.is_valid():
            updated_image = form.save()

            new_file_name = (
                updated_image.image.name
                if updated_image.image else None
            )

            if old_file_name and old_file_name != new_file_name:
                transaction.on_commit(
                    lambda: _delete_gallery_file_if_unused(
                        old_storage,
                        old_file_name,
                    )
                )

            messages.success(
                request,
                f'"{updated_image.title}" was updated successfully.'
            )
            return redirect("dashboard:gallery_list")
    else:
        form = GalleryImageForm(instance=image)

    return render(request, "dashboard/gallery/form.html", {
        "form": form,
        "page_title": "Edit Gallery Image",
        "button_label": "Save Changes",
        "gallery_image": image,
    })


@staff_required
def gallery_delete(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)

    if request.method == "POST":
        title = image.title
        file_name = image.image.name if image.image else None
        storage = image.image.storage if image.image else None

        image.delete()

        if file_name:
            transaction.on_commit(
                lambda: _delete_gallery_file_if_unused(
                    storage,
                    file_name,
                )
            )

        messages.success(
            request,
            f'"{title}" was deleted successfully.'
        )
        return redirect("dashboard:gallery_list")

    return render(request, "dashboard/gallery/confirm_delete.html", {
        "gallery_image": image,
    })


# --------------------------------------------------
# EVENTS MANAGEMENT
# --------------------------------------------------

def _delete_event_file_if_unused(storage, file_name):
    if file_name and not Event.objects.filter(
        image=file_name
    ).exists():
        storage.delete(file_name)


@staff_required
def event_list(request):
    events = Event.objects.all()
    return render(request, "dashboard/events/list.html", {
        "events": events,
    })


@staff_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save()
            messages.success(
                request,
                f'"{event.title}" was added successfully.'
            )
            return redirect("dashboard:event_list")
    else:
        form = EventForm()

    return render(request, "dashboard/events/form.html", {
        "form": form,
        "page_title": "Add Clinic Event",
        "button_label": "Save Event",
    })


@staff_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    old_file_name = event.image.name if event.image else None
    old_storage = event.image.storage if event.image else None

    if request.method == "POST":
        form = EventForm(
            request.POST,
            request.FILES,
            instance=event,
        )

        if form.is_valid():
            updated_event = form.save()

            new_file_name = (
                updated_event.image.name
                if updated_event.image else None
            )

            if old_file_name and old_file_name != new_file_name:
                transaction.on_commit(
                    lambda: _delete_event_file_if_unused(
                        old_storage,
                        old_file_name,
                    )
                )

            messages.success(
                request,
                f'"{updated_event.title}" was updated successfully.'
            )
            return redirect("dashboard:event_list")
    else:
        form = EventForm(instance=event)

    return render(request, "dashboard/events/form.html", {
        "form": form,
        "page_title": "Edit Clinic Event",
        "button_label": "Save Changes",
        "event": event,
    })


@staff_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        title = event.title
        file_name = event.image.name if event.image else None
        storage = event.image.storage if event.image else None

        event.delete()

        if file_name:
            transaction.on_commit(
                lambda: _delete_event_file_if_unused(
                    storage,
                    file_name,
                )
            )

        messages.success(
            request,
            f'"{title}" was deleted successfully.'
        )
        return redirect("dashboard:event_list")

    return render(request, "dashboard/events/confirm_delete.html", {
        "event": event,
    })

# --------------------------------------------------
# HOMEPAGE CONTENT MANAGEMENT
# --------------------------------------------------

@staff_required
def homepage_content_edit(request):
    homepage_content, created = HomepageContent.objects.get_or_create(pk=1)

    if request.method == "POST":
        form = HomepageContentForm(
            request.POST,
            instance=homepage_content,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Homepage content was updated successfully."
            )
            return redirect("dashboard:homepage_content_edit")
    else:
        form = HomepageContentForm(instance=homepage_content)

    return render(request, "dashboard/homepage_content/form.html", {
        "form": form,
        "page_title": "Manage Homepage Content",
        "button_label": "Save Homepage Content",
    })



# --------------------------------------------------
# APPOINTMENT MANAGEMENT
# --------------------------------------------------

def _appointment_whatsapp_url(appointment):
    from urllib.parse import quote
    from core.models import Appointment

    phone = "".join(
        character
        for character in appointment.contact_number
        if character.isdigit()
    )

    if phone.startswith("0"):
        phone = "27" + phone[1:]

    if len(phone) < 10:
        return ""

    flower = "\U0001F338"
    calendar = "\U0001F4C5"
    clock = "\U0001F552"
    bookmark = "\U0001F516"
    phone_icon = "\U0001F4DE"

    if (
        appointment.status in [
            Appointment.Status.CONFIRMED,
            Appointment.Status.RESCHEDULED,
        ]
        and appointment.confirmed_date
        and appointment.confirmed_time
    ):
        message = (
            f"Good day, {appointment.patient_name}! {flower}\n\n"
            "Thank you for booking with Injabulo Clinic.\n\n"
            "We are pleased to confirm that your appointment "
            "has been successfully booked.\n\n"
            f"{calendar} Appointment date: "
            f"{appointment.confirmed_date.strftime('%d %b %Y')}\n"
            f"{clock} Appointment time: "
            f"{appointment.confirmed_time.strftime('%H:%M')}\n"
            f"{bookmark} Booking reference: #{appointment.pk}\n\n"
            "We look forward to welcoming you to our clinic "
            "and providing you with quality care.\n\n"
            "Thank you for choosing Injabulo Clinic.\n\n"
            "Kind regards,\n"
            "Injabulo Clinic Team\n"
            f"{phone_icon} 012 800 1903"
        )
    else:
        message = (
            f"Good day, {appointment.patient_name}! {flower}\n\n"
            "Thank you for booking with Injabulo Clinic.\n\n"
            "We have successfully received your appointment request.\n"
            f"Booking reference: #{appointment.pk}\n\n"
            "Our team will review your booking and contact you "
            "regarding your appointment confirmation.\n\n"
            "Thank you for choosing Injabulo Clinic.\n"
            f"{phone_icon} 012 800 1903"
        )

    return f"https://wa.me/{phone}?text={quote(message, safe='')}"


@staff_required
def appointment_list(request):
    from django.db.models import Q
    from core.models import Appointment

    appointments = Appointment.objects.select_related(
        "service"
    ).all()

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        appointments = appointments.filter(
            Q(patient_name__icontains=search) |
            Q(contact_number__icontains=search) |
            Q(service__title__icontains=search)
        )

    valid_statuses = dict(Appointment.Status.choices)

    if status in valid_statuses:
        appointments = appointments.filter(status=status)
    else:
        status = ""

    upcoming = request.GET.get("upcoming") == "1"
    if upcoming:
        from django.utils import timezone
        appointments = appointments.filter(
            status__in=[
                Appointment.Status.CONFIRMED,
                Appointment.Status.RESCHEDULED,
            ],
            confirmed_date__isnull=False,
            confirmed_date__gte=timezone.localdate(),
        )

    appointments = appointments.order_by("-created_at")

    for appointment in appointments:
        appointment.whatsapp_url = _appointment_whatsapp_url(appointment)

    context = {
        "appointments": appointments,
        "search": search,
        "selected_status": status,
        "upcoming_only": upcoming,
        "total_appointments": Appointment.objects.count(),
        "pending_appointments": Appointment.objects.filter(
            status=Appointment.Status.PENDING
        ).count(),
        "confirmed_appointments": Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED
        ).count(),
        "rescheduled_appointments": Appointment.objects.filter(
            status=Appointment.Status.RESCHEDULED
        ).count(),
        "completed_appointments": Appointment.objects.filter(
            status=Appointment.Status.COMPLETED
        ).count(),
    }

    return render(
        request,
        "dashboard/appointments/list.html",
        context
    )


@staff_required
@require_POST
def appointment_update(request, pk):
    from core.models import Appointment
    from django.utils.dateparse import parse_date, parse_time

    appointment = get_object_or_404(Appointment, pk=pk)

    status = request.POST.get("status", "")
    valid_statuses = dict(Appointment.Status.choices)

    if status not in valid_statuses:
        messages.error(request, "Please select a valid appointment status.")
        return redirect("dashboard:appointment_list")

    confirmed_date_input = request.POST.get(
        "confirmed_date", ""
    ).strip()

    confirmed_time_input = request.POST.get(
        "confirmed_time", ""
    ).strip()

    confirmed_date = (
        parse_date(confirmed_date_input)
        if confirmed_date_input else None
    )

    confirmed_time = (
        parse_time(confirmed_time_input)
        if confirmed_time_input else None
    )

    if confirmed_date_input and confirmed_date is None:
        messages.error(request, "Please enter a valid confirmed date.")
        return redirect("dashboard:appointment_list")

    if confirmed_time_input and confirmed_time is None:
        messages.error(request, "Please enter a valid confirmed time.")
        return redirect("dashboard:appointment_list")

    if status in [
        Appointment.Status.CONFIRMED,
        Appointment.Status.RESCHEDULED,
    ] and (not confirmed_date or not confirmed_time):
        messages.error(
            request,
            "Please enter both the confirmed appointment date and time."
        )
        return redirect("dashboard:appointment_list")

    appointment.status = status
    appointment.confirmed_date = confirmed_date
    appointment.confirmed_time = confirmed_time
    appointment.save()

    messages.success(
        request,
        f"Appointment #{appointment.pk} was updated successfully."
    )

    return redirect("dashboard:appointment_list")

# --------------------------------------------------
# PATIENT COMMUNICATION AND APPOINTMENT DETAILS
# --------------------------------------------------

from django.utils import timezone


@staff_required
def appointment_detail(request, pk):
    from core.models import Appointment

    appointment = get_object_or_404(
        Appointment.objects.select_related("service"),
        pk=pk
    )

    return render(
        request,
        "dashboard/appointments/detail.html",
        {
            "appointment": appointment,
            "whatsapp_url": _appointment_whatsapp_url(appointment),
        }
    )


@staff_required
@require_POST
def appointment_mark_contacted(request, pk):
    from core.models import Appointment

    appointment = get_object_or_404(Appointment, pk=pk)

    appointment.communication_status = (
        Appointment.CommunicationStatus.CONTACTED
    )
    appointment.contacted_at = timezone.now()

    appointment.save(
        update_fields=[
            "communication_status",
            "contacted_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Appointment #{appointment.pk} marked as contacted."
    )

    return redirect("dashboard:appointment_list")


# --------------------------------------------------
# HEALTH EDUCATION VIDEO MANAGEMENT
# --------------------------------------------------

def _delete_video_file_if_unused(storage, file_name, field_name):
    if file_name and not Video.objects.filter(
        **{field_name: file_name}
    ).exists():
        storage.delete(file_name)


@staff_required
def video_list(request):
    videos = Video.objects.all()
    return render(request, "dashboard/videos/list.html", {
        "videos": videos,
    })


@staff_required
def video_create(request):
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            messages.success(
                request,
                f'"{video.title}" was uploaded successfully.'
            )
            return redirect("dashboard:video_list")
    else:
        form = VideoForm()

    return render(request, "dashboard/videos/form.html", {
        "form": form,
        "page_title": "Upload Health Education Video",
        "button_label": "Upload Video",
    })


@staff_required
def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)

    old_video_name = video.video_file.name if video.video_file else None
    old_video_storage = video.video_file.storage if video.video_file else None
    old_thumbnail_name = video.thumbnail.name if video.thumbnail else None
    old_thumbnail_storage = video.thumbnail.storage if video.thumbnail else None

    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES, instance=video)

        if form.is_valid():
            updated_video = form.save()

            new_video_name = (
                updated_video.video_file.name
                if updated_video.video_file else None
            )
            new_thumbnail_name = (
                updated_video.thumbnail.name
                if updated_video.thumbnail else None
            )

            if old_video_name and old_video_name != new_video_name:
                transaction.on_commit(
                    lambda: _delete_video_file_if_unused(
                        old_video_storage,
                        old_video_name,
                        "video_file",
                    )
                )

            if old_thumbnail_name and old_thumbnail_name != new_thumbnail_name:
                transaction.on_commit(
                    lambda: _delete_video_file_if_unused(
                        old_thumbnail_storage,
                        old_thumbnail_name,
                        "thumbnail",
                    )
                )

            messages.success(
                request,
                f'"{updated_video.title}" was updated successfully.'
            )
            return redirect("dashboard:video_list")
    else:
        form = VideoForm(instance=video)

    return render(request, "dashboard/videos/form.html", {
        "form": form,
        "page_title": "Edit Health Education Video",
        "button_label": "Save Changes",
        "video": video,
    })


@staff_required
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)

    if request.method == "POST":
        title = video.title
        video_name = video.video_file.name if video.video_file else None
        video_storage = video.video_file.storage if video.video_file else None
        thumbnail_name = video.thumbnail.name if video.thumbnail else None
        thumbnail_storage = video.thumbnail.storage if video.thumbnail else None

        video.delete()

        if video_name:
            transaction.on_commit(
                lambda: _delete_video_file_if_unused(
                    video_storage,
                    video_name,
                    "video_file",
                )
            )

        if thumbnail_name:
            transaction.on_commit(
                lambda: _delete_video_file_if_unused(
                    thumbnail_storage,
                    thumbnail_name,
                    "thumbnail",
                )
            )

        messages.success(request, f'"{title}" was deleted successfully.')
        return redirect("dashboard:video_list")

    return render(request, "dashboard/videos/confirm_delete.html", {
        "video": video,
    })



@staff_required
def corporate_enquiry_list(request):
    from django.db.models import Q

    enquiries = CorporateEnquiry.objects.all()
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        enquiries = enquiries.filter(
            Q(company_name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    valid_statuses = dict(CorporateEnquiry.STATUS_CHOICES)
    if status in valid_statuses:
        enquiries = enquiries.filter(status=status)
    else:
        status = ""

    context = {
        "enquiries": enquiries,
        "search": search,
        "selected_status": status,
        "status_choices": CorporateEnquiry.STATUS_CHOICES,
        "total_enquiries": CorporateEnquiry.objects.count(),
        "new_enquiries": CorporateEnquiry.objects.filter(status="new").count(),
        "contacted_enquiries": CorporateEnquiry.objects.filter(status="contacted").count(),
        "quoted_enquiries": CorporateEnquiry.objects.filter(status="quoted").count(),
        "approved_enquiries": CorporateEnquiry.objects.filter(status="approved").count(),
        "completed_enquiries": CorporateEnquiry.objects.filter(status="completed").count(),
    }

    return render(request, "dashboard/corporate_enquiries/list.html", context)


@staff_required
@require_POST
def corporate_enquiry_update(request, pk):
    enquiry = get_object_or_404(CorporateEnquiry, pk=pk)

    new_status = request.POST.get("status", "").strip()
    staff_notes = request.POST.get("staff_notes", "")

    valid_statuses = dict(CorporateEnquiry.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Please select a valid enquiry status.")
        return redirect("dashboard:corporate_enquiry_list")

    enquiry.status = new_status
    enquiry.staff_notes = staff_notes
    enquiry.save(update_fields=["status", "staff_notes", "updated_at"])

    messages.success(
        request,
        f'Enquiry for "{enquiry.company_name}" was updated successfully.'
    )
    return redirect("dashboard:corporate_enquiry_list")


@staff_required
def corporate_quotation_list(request):
    from django.db.models import Q

    quotations = CorporateQuotation.objects.select_related(
        "enquiry"
    ).prefetch_related("items")

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        quotations = quotations.filter(
            Q(reference__icontains=search) |
            Q(enquiry__company_name__icontains=search)
        )

    valid_statuses = dict(CorporateQuotation.STATUS_CHOICES)
    if status in valid_statuses:
        quotations = quotations.filter(status=status)
    else:
        status = ""

    context = {
        "quotations": quotations,
        "search": search,
        "selected_status": status,
        "status_choices": CorporateQuotation.STATUS_CHOICES,
        "total_quotations": CorporateQuotation.objects.count(),
        "draft_quotations": CorporateQuotation.objects.filter(status="draft").count(),
        "sent_quotations": CorporateQuotation.objects.filter(status="sent").count(),
        "accepted_quotations": CorporateQuotation.objects.filter(status="accepted").count(),
    }

    return render(request, "dashboard/corporate_quotations/list.html", context)


@staff_required
def corporate_quotation_create(request):
    from django.forms import formset_factory
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    from uuid import uuid4

    ItemFormSet = formset_factory(
        CorporateQuotationItemForm,
        extra=3,
        can_delete=True,
        max_num=20,
        validate_max=True,
    )

    today = timezone.localdate()

    if request.method == "POST":
        form = CorporateQuotationForm(request.POST)
        item_formset = ItemFormSet(request.POST, prefix="items")

        if form.is_valid() and item_formset.is_valid():
            valid_items = [
                item_form.cleaned_data
                for item_form in item_formset
                if item_form.cleaned_data
                and not item_form.cleaned_data.get("DELETE", False)
            ]

            if not valid_items:
                messages.error(request, "Add at least one valid quotation service item.")
            else:
                quotation = form.save(commit=False)
                quotation.reference = (
                    f"ICQ-{today:%Y%m%d}-{uuid4().hex[:6].upper()}"
                )
                quotation.subtotal = sum(
                    (
                        item["quantity"] * item["unit_price"]
                        for item in valid_items
                    ),
                    Decimal("0.00"),
                )
                quotation.save()

                for item_data in valid_items:
                    CorporateQuotationItem.objects.create(
                        quotation=quotation,
                        description=item_data["description"],
                        quantity=item_data["quantity"],
                        unit_price=item_data["unit_price"],
                        line_total=item_data["quantity"] * item_data["unit_price"],
                    )

                messages.success(
                    request,
                    f"Quotation {quotation.reference} created successfully."
                )
                return redirect("dashboard:corporate_quotation_list")
    else:
        form = CorporateQuotationForm(initial={
            "issue_date": today,
            "valid_until": today + timedelta(days=14),
            "status": "draft",
        })
        item_formset = ItemFormSet(prefix="items")

    return render(request, "dashboard/corporate_quotations/form.html", {
        "form": form,
        "item_formset": item_formset,
        "page_title": "Create Corporate Quotation",
    })


@staff_required
@require_POST
def corporate_quotation_update_status(request, pk):
    quotation = get_object_or_404(CorporateQuotation, pk=pk)
    new_status = request.POST.get("status", "").strip()

    valid_statuses = dict(CorporateQuotation.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Please select a valid quotation status.")
    else:
        quotation.status = new_status
        quotation.save(update_fields=["status", "updated_at"])
        messages.success(
            request,
            f"Quotation {quotation.reference} updated successfully."
        )

    return redirect("dashboard:corporate_quotation_list")


@staff_required
def corporate_quotation_pdf(request, pk):
    quotation = get_object_or_404(
        CorporateQuotation.objects.select_related("enquiry").prefetch_related("items"),
        pk=pk,
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{quotation.reference}.pdf"'
    )

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    teal = colors.HexColor("#278B91")
    dark = colors.HexColor("#292929")
    muted = colors.HexColor("#666666")

    styles.add(ParagraphStyle(
        name="ClinicTitle",
        parent=styles["Title"],
        textColor=teal,
        fontSize=22,
        leading=27,
        alignment=0,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="SmallMuted",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=muted,
    ))
    styles.add(ParagraphStyle(
        name="RightText",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
        fontSize=9,
        leading=13,
    ))

    story = []

    logo_path = (
        Path(settings.BASE_DIR)
        / "core" / "static" / "core" / "images"
        / "injabulo-clinic-logo.png"
    )

    if logo_path.exists():
        logo = Image(str(logo_path), width=38 * mm, height=25 * mm)
        logo.hAlign = "LEFT"
        story.append(logo)

    story.append(Paragraph("INJABULO CLINIC", styles["ClinicTitle"]))
    story.append(Paragraph(
        "18 Stapelberg Ave, East Lynne, Pretoria, 0186<br/>"
        "Telephone: 012 800 1903 | WhatsApp: 079 399 6635<br/>"
        "Email: injabuloclinics@gmail.com<br/>"
        "Professional Nurse: Sr H.G. Fankomo",
        styles["SmallMuted"],
    ))
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("CORPORATE SERVICE QUOTATION", styles["Heading1"]))
    story.append(Spacer(1, 4 * mm))

    company = quotation.enquiry

    details = [
        ["Quotation Reference", quotation.reference],
        ["Company", company.company_name],
        ["Contact Person", company.contact_person],
        ["Email", company.email],
        ["Telephone", company.phone],
        ["Service Location", company.service_location],
        ["Issue Date", quotation.issue_date.strftime("%d %B %Y")],
        ["Valid Until", quotation.valid_until.strftime("%d %B %Y")],
    ]

    details_table = Table(details, colWidths=[48 * mm, 118 * mm])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF4F3")),
        ("TEXTCOLOR", (0, 0), (0, -1), teal),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 9 * mm))

    story.append(Paragraph("SERVICE BREAKDOWN", styles["Heading2"]))

    item_data = [[
        "Description", "Quantity", "Unit Price (R)", "Total (R)"
    ]]

    for item in quotation.items.all():
        item_data.append([
            Paragraph(item.description.replace("&", "&amp;"), styles["Normal"]),
            str(item.quantity),
            f"R {item.unit_price:,.2f}",
            f"R {item.line_total:,.2f}",
        ])

    item_table = Table(
        item_data,
        colWidths=[82 * mm, 22 * mm, 34 * mm, 34 * mm],
        repeatRows=1,
    )
    item_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), teal),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white, colors.HexColor("#F5F8F7")
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 5 * mm))

    total_table = Table(
        [["SUBTOTAL", f"R {quotation.subtotal:,.2f}"]],
        colWidths=[138 * mm, 34 * mm],
    )
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF4F3")),
        ("TEXTCOLOR", (0, 0), (-1, -1), teal),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    story.append(total_table)

    if quotation.notes:
        story.append(Spacer(1, 8 * mm))
        story.append(Paragraph("ADDITIONAL TERMS AND NOTES", styles["Heading2"]))
        story.append(Paragraph(
            quotation.notes.replace("&", "&amp;").replace("\n", "<br/>"),
            styles["Normal"],
        ))

    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph("QUOTATION ACCEPTANCE", styles["Heading2"]))
    story.append(Paragraph(
        "I confirm that I am authorised to accept this quotation on behalf "
        "of the company named above.",
        styles["SmallMuted"],
    ))
    story.append(Spacer(1, 12 * mm))

    signature_data = [
        ["Authorised Name: __________________________", "Date: __________________"],
        ["Signature: ________________________________", "Company Stamp:"],
    ]
    signature_table = Table(
        signature_data,
        colWidths=[105 * mm, 67 * mm],
        rowHeights=[15 * mm, 18 * mm],
    )
    signature_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEBELOW", (0, 0), (0, 0), 0.5, muted),
        ("LINEBELOW", (1, 0), (1, 0), 0.5, muted),
    ]))
    story.append(signature_table)
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "Thank you for considering Injabulo Clinic for your corporate "
        "healthcare needs.",
        styles["SmallMuted"],
    ))

    document.build(story)
    response.write(buffer.getvalue())
    buffer.close()
    return response


# ==========================================================
# BLOG MANAGEMENT
# ==========================================================

@staff_required
def blog_list(request):
    posts = BlogPost.objects.all()
    return render(request, "dashboard/blog/list.html", {"posts": posts})


@staff_required
def blog_create(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            messages.success(request, f'"{post.title}" was saved successfully.')
            return redirect("dashboard:blog_list")
    else:
        form = BlogPostForm()

    return render(request, "dashboard/blog/form.html", {
        "form": form,
        "page_title": "Create Blog Article",
        "button_label": "Save Article",
    })


@staff_required
def blog_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog article updated successfully.")
            return redirect("dashboard:blog_list")
    else:
        form = BlogPostForm(instance=post)

    return render(request, "dashboard/blog/form.html", {
        "form": form,
        "page_title": "Edit Blog Article",
        "button_label": "Save Changes",
    })


@staff_required
@require_POST
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.delete()
    messages.success(request, "Blog article deleted.")
    return redirect("dashboard:blog_list")


# ==========================================================
# HEALTHCARE TEAM MANAGEMENT
# ==========================================================

@staff_required
def team_list(request):
    members = TeamMember.objects.all()
    return render(request, "dashboard/team/list.html", {
        "members": members,
    })


@staff_required
def team_create(request):
    if request.method == "POST":
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"{member.full_name} was added to the team.")
            return redirect("dashboard:team_list")
    else:
        form = TeamMemberForm()

    return render(request, "dashboard/team/form.html", {
        "form": form,
        "page_title": "Add Team Member",
        "button_label": "Save Team Member",
    })


@staff_required
def team_edit(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == "POST":
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Team profile updated.")
            return redirect("dashboard:team_list")
    else:
        form = TeamMemberForm(instance=member)

    return render(request, "dashboard/team/form.html", {
        "form": form,
        "page_title": "Edit Team Member",
        "button_label": "Save Changes",
    })


@staff_required
@require_POST
def team_delete(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    member.delete()
    messages.success(request, "Team member deleted.")
    return redirect("dashboard:team_list")



@staff_required
@require_POST
def notification_open(request, pk):
    notification = get_object_or_404(
        DashboardNotification.objects.select_related("appointment"),
        pk=pk,
    )
    notification.is_read = True
    notification.save(update_fields=["is_read"])

    return redirect(
        "dashboard:appointment_detail",
        pk=notification.appointment_id,
    )

# --------------------------------------------------
# APPOINTMENT HISTORY AND MONTHLY REPORTS
# --------------------------------------------------

from datetime import date
from django.db.models import Count
from django.utils import timezone




@staff_required
def appointment_monthly_report_pdf(request):
    from core.models import Appointment
    from xml.sax.saxutils import escape

    today = timezone.localdate()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

        if month < 1 or month > 12 or year < 2000 or year > today.year:
            raise ValueError
    except (TypeError, ValueError):
        year = today.year
        month = today.month

    start_date = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    appointments = Appointment.objects.filter(
        preferred_date__gte=start_date,
        preferred_date__lt=next_month,
    )

    status_counts = {
        value: appointments.filter(status=value).count()
        for value, label in Appointment.Status.choices
    }

    contacted = appointments.filter(
        communication_status=Appointment.CommunicationStatus.CONTACTED
    ).count()

    not_contacted = appointments.filter(
        communication_status=Appointment.CommunicationStatus.NOT_CONTACTED
    ).count()

    service_counts = (
        appointments
        .values("service__title")
        .annotate(total=Count("id"))
        .order_by("-total", "service__title")
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Injabulo_Appointment_Report_{year}_{month:02d}.pdf"'
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    teal = colors.HexColor("#278B91")
    dark = colors.HexColor("#292929")
    muted = colors.HexColor("#666666")

    styles.add(ParagraphStyle(
        name="AppointmentClinicTitle",
        parent=styles["Title"],
        textColor=teal,
        fontSize=22,
        leading=27,
        alignment=0,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="AppointmentSmall",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=muted,
    ))

    story = []

    logo_path = (
        Path(settings.BASE_DIR)
        / "core" / "static" / "core" / "images"
        / "injabulo-clinic-logo.png"
    )

    if logo_path.exists():
        logo = Image(str(logo_path), width=38 * mm, height=25 * mm)
        logo.hAlign = "LEFT"
        story.append(logo)

    story.append(Paragraph(
        "INJABULO CLINIC",
        styles["AppointmentClinicTitle"]
    ))

    story.append(Paragraph(
        "18 Stapelberg Ave, East Lynne, Pretoria, 0186<br/>"
        "Telephone: 012 800 1903 | WhatsApp: 079 399 6635<br/>"
        "Email: injabuloclinics@gmail.com",
        styles["AppointmentSmall"],
    ))

    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph(
        "MONTHLY APPOINTMENT REPORT",
        styles["Heading1"]
    ))

    story.append(Paragraph(
        f"Reporting period: {start_date.strftime('%B %Y')}",
        styles["Heading2"]
    ))

    story.append(Paragraph(
        f"Generated: {timezone.localtime().strftime('%d %B %Y, %H:%M')}",
        styles["AppointmentSmall"]
    ))

    story.append(Spacer(1, 6 * mm))

    summary = [
        ["APPOINTMENT STATISTICS", "TOTAL"],
        ["Total Requests", appointments.count()],
        ["Pending", status_counts.get("pending", 0)],
        ["Confirmed", status_counts.get("confirmed", 0)],
        ["Rescheduled", status_counts.get("rescheduled", 0)],
        ["Completed", status_counts.get("completed", 0)],
        ["Declined", status_counts.get("declined", 0)],
        ["Patients Contacted", contacted],
        ["Not Contacted", not_contacted],
    ]

    summary_table = Table(summary, colWidths=[115 * mm, 45 * mm])

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), teal),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 1), (-1, -1), dark),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F3F7F5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("SERVICES BOOKED", styles["Heading2"]))

    service_data = [["Clinic Service", "Appointment Requests"]]

    for item in service_counts:
        service_name = escape(item["service__title"] or "Unspecified")
        service_data.append([service_name, item["total"]])

    if len(service_data) == 1:
        service_data.append(["No service bookings recorded", 0])

    service_table = Table(
        service_data,
        colWidths=[115 * mm, 45 * mm],
        repeatRows=1,
    )

    service_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), teal),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F3F7F5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(service_table)
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph(
        "Confidential clinic management report.",
        styles["AppointmentSmall"]
    ))

    document.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)
    return response


@staff_required
def appointment_history(request):
    from core.models import Appointment

    appointments = Appointment.objects.select_related("service").all()

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        appointments = appointments.filter(
            patient_name__icontains=search
        ) | appointments.filter(
            contact_number__icontains=search
        ) | appointments.filter(
            service__title__icontains=search
        )

    valid_statuses = dict(Appointment.Status.choices)
    if status in valid_statuses:
        appointments = appointments.filter(status=status)
    else:
        status = ""

    appointments = appointments.order_by(
        "-preferred_date", "-preferred_time", "-created_at"
    )

    return render(
        request,
        "dashboard/appointments/history.html",
        {
            "appointments": appointments,
            "search": search,
            "selected_status": status,
            "history_count": appointments.count(),
        },
    )


@staff_required
def appointment_monthly_report(request):
    from core.models import Appointment

    today = timezone.localdate()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

        if month < 1 or month > 12 or year < 2000 or year > today.year:
            raise ValueError

    except (TypeError, ValueError):
        year = today.year
        month = today.month

    start_date = date(year, month, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    monthly_appointments = Appointment.objects.filter(
        preferred_date__gte=start_date,
        preferred_date__lt=next_month,
    )

    status_counts = {
        value: monthly_appointments.filter(status=value).count()
        for value, label in Appointment.Status.choices
    }

    service_counts = (
        monthly_appointments
        .values("service__title")
        .annotate(total=Count("id"))
        .order_by("-total", "service__title")
    )

    month_choices = [
        (number, date(2000, number, 1).strftime("%B"))
        for number in range(1, 13)
    ]

    context = {
        "selected_year": year,
        "selected_month": month,
        "month_name": start_date.strftime("%B"),
        "month_choices": month_choices,
        "total_appointments": monthly_appointments.count(),
        "pending_appointments": status_counts.get("pending", 0),
        "confirmed_appointments": status_counts.get("confirmed", 0),
        "rescheduled_appointments": status_counts.get("rescheduled", 0),
        "declined_appointments": status_counts.get("declined", 0),
        "completed_appointments": status_counts.get("completed", 0),
        "contacted_appointments": monthly_appointments.filter(
            communication_status=Appointment.CommunicationStatus.CONTACTED
        ).count(),
        "not_contacted_appointments": monthly_appointments.filter(
            communication_status=Appointment.CommunicationStatus.NOT_CONTACTED
        ).count(),
        "service_counts": service_counts,
        "available_years": range(
            today.year, max(2000, today.year - 10) - 1, -1
        ),
    }

    return render(
        request,
        "dashboard/appointments/monthly_report.html",
        context,
    )


from datetime import date
from django.db.models import Count
from django.utils import timezone
