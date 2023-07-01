from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_project.sitemaps import (
    PostSitemap,
    HomeSitemap,
    WorksCitedSiteMap,
    privacyPolicySiteMap,
    CategorySitemap,
    PortfolioSiteMap,
    StatusPageSiteMap,
)
from .views import (
    works_cited_view,
    privacy_view,
    security_txt_view,
    security_pgp_key_view,
)
from users.views import (
    register_view,
    profile_view,
    MyLoginView,
    MyLogoutView,
    MyPasswordResetView,
    MyPasswordResetDoneView,
    MyPasswordResetConfirmView,
    MyPasswordResetCompleteView,
)

sitemaps = {
    "posts": PostSitemap,
    "home page": HomeSitemap,
    "Works Cited": WorksCitedSiteMap,
    "Privacy Policy": privacyPolicySiteMap,
    "Categories": CategorySitemap,
    "Portfolio": PortfolioSiteMap,
    "Status Page": StatusPageSiteMap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("works-cited", works_cited_view, name="works-cited"),
    path("privacy", privacy_view, name="privacy"),
    path("admin/", admin.site.urls),
    path(".well-known/security.txt", security_txt_view, name="security-txt"),
    path("pgp-key.txt", security_pgp_key_view, name="security-pgp-key-txt"),
    path("robots.txt", include("robots.urls")),
    path("", include("blog.urls")),
    path("register/", register_view, name="register"),
    path("profile/", profile_view, name="profile"),
    path(
        "login/",
        MyLoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        MyLogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path(
        "password-reset/",
        MyPasswordResetView.as_view(template_name="users/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        MyPasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        MyPasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        MyPasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("captcha", include("captcha.urls")),
]
if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
