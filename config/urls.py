from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from core.views import service_worker

urlpatterns = [
    path('service-worker.js', service_worker, name='service_worker'),
    path("admin/", admin.site.urls),
    path("services/", include("services.urls")),
    path("gallery/", include("gallery.urls")),
    path("events/", include("events.urls")),
    path("videos/", include("videos.urls")),
    path("health-blog/", include("blog.urls")),
    path("our-team/", include("team.urls")),
    path("corporate-wellness/", include("corporate.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("core.urls")),
]

urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
