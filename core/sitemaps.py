from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from services.models import Service
from blog.models import BlogPost


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "contact",
            "appointment",
            "services:service_list",
            "blog:post_list",
            "events:event_list",
            "gallery:gallery_list",
            "team:team_list",
            "corporate:corporate_wellness",
            "videos:video_library",
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("services:service_detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.created_at


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("blog:post_detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at

