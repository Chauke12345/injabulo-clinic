from django.urls import path
from . import views

app_name = "corporate"

urlpatterns = [
    path("", views.corporate_wellness, name="corporate_wellness"),
]
