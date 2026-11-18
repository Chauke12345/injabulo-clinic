from django.urls import path
from . import views

app_name = "testimonials"

urlpatterns = [
    path("submit/", views.submit_testimonial, name="submit_testimonial"),
]
