from django.urls import path, include
from .views import (
    register_view,
    profile_view,
    MyLoginView,
    MyLogoutView,
    MyPasswordResetView,
    MyPasswordResetDoneView,
    MyPasswordResetConfirmView,
    MyPasswordResetCompleteView,
)

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
