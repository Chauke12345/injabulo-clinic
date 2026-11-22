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
