from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("appointments/", views.appointment, name="appointment"),
    path("booking-app/", views.booking_app, name="booking_app"),
    path("booking-app/preview/", views.booking_app_preview, name="booking_app_preview"),
]
