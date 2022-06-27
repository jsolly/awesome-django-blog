"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_project.sitemaps import (
    PostSitemap,
    HomeSitemap,
    WorksCitedSiteMap,
    RoadmapSitemap,
    CategorySiteMap,
    SiteAnalyticsSiteMap,
)
from .views import (
    road_map_view,
    works_cited_view,
    security_txt_view,
    security_pgp_key_view,
)
from siteanalytics.views import site_analytics_view


sitemaps = {
    "posts": PostSitemap,
    "categories": CategorySiteMap,
    "home page": HomeSitemap,
    "Site Analytics": SiteAnalyticsSiteMap,
    "Roadmap": RoadmapSitemap,
    "Works Cited": WorksCitedSiteMap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("works-cited", works_cited_view, name="blog-works-cited"),
    path("siteanalytics", site_analytics_view, name="blog-site-analytics"),
    path("roadmap/", road_map_view, name="blog-roadmap"),
    path("admin/", admin.site.urls),
    path(".well-known/security.txt", security_txt_view, name="security-txt"),
    path("pgp-key.txt", security_pgp_key_view, name="security-pgp-key-txt"),
    path("robots.txt", include("robots.urls")),
    path("", include("blog.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
