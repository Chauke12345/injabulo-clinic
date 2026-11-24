from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "dashboard"

urlpatterns = [
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/create/", views.blog_create, name="blog_create"),
    path("blog/<int:pk>/edit/", views.blog_edit, name="blog_edit"),
    path("blog/<int:pk>/delete/", views.blog_delete, name="blog_delete"),
    path("team/", views.team_list, name="team_list"),
    path("team/create/", views.team_create, name="team_create"),
    path("team/<int:pk>/edit/", views.team_edit, name="team_edit"),
    path("team/<int:pk>/delete/", views.team_delete, name="team_delete"),

    path(
        "login/",
        views.RoleBasedLoginView.as_view(
            template_name="dashboard/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("", views.dashboard_home, name="home"),
    path(
        "homepage/",
        views.homepage_content_edit,
        name="homepage_content_edit",
    ),

    # Clinic services management
    path("services/", views.service_list, name="service_list"),
    path("services/add/", views.service_create, name="service_create"),
    path("services/<int:pk>/edit/", views.service_edit, name="service_edit"),
    path("services/<int:pk>/delete/", views.service_delete, name="service_delete"),

    # Gallery management
    path("gallery/", views.gallery_list, name="gallery_list"),
    path("gallery/add/", views.gallery_create, name="gallery_create"),
    path("gallery/<int:pk>/edit/", views.gallery_edit, name="gallery_edit"),
    path("gallery/<int:pk>/delete/", views.gallery_delete, name="gallery_delete"),

    # Events management
    path("events/", views.event_list, name="event_list"),
    path("events/add/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    # Health education video management
    path("videos/", views.video_list, name="video_list"),
    path("videos/add/", views.video_create, name="video_create"),
    path("videos/<int:pk>/edit/", views.video_edit, name="video_edit"),
    path("videos/<int:pk>/delete/", views.video_delete, name="video_delete"),


    # Corporate Wellness enquiry management
    path("corporate-enquiries/", views.corporate_enquiry_list, name="corporate_enquiry_list"),
    path("corporate-enquiries/<int:pk>/update/", views.corporate_enquiry_update, name="corporate_enquiry_update"),


    # Corporate quotation management
    path("corporate-quotations/", views.corporate_quotation_list, name="corporate_quotation_list"),
    path("corporate-quotations/create/", views.corporate_quotation_create, name="corporate_quotation_create"),
    path("corporate-quotations/<int:pk>/pdf/", views.corporate_quotation_pdf, name="corporate_quotation_pdf"),
    path("corporate-quotations/<int:pk>/status/", views.corporate_quotation_update_status, name="corporate_quotation_update_status"),

    # Appointment management
    path("notifications/<int:pk>/open/", views.notification_open, name="notification_open"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/history/", views.appointment_history, name="appointment_history"),
    path("appointments/monthly-report/", views.appointment_monthly_report, name="appointment_monthly_report"),
    path("appointments/monthly-report/pdf/", views.appointment_monthly_report_pdf, name="appointment_monthly_report_pdf"),
    path("appointments/<int:pk>/update/", views.appointment_update, name="appointment_update"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:pk>/mark-contacted/", views.appointment_mark_contacted, name="appointment_mark_contacted"),
]



