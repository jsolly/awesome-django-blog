from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            secret_password = form.cleaned_data.get("secret_password")
            if secret_password != "African Swallows":
                messages.error(request, "Hmm, I don't think that is the right password")
            else:
                form.save()
                username = form.cleaned_data.get("username")
                messages.success(request, f"Account created for {username}")
                return redirect("login")

    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile_view(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated")
            return redirect("profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "users/profile.html", context=context)


class MyLoginView(auth_views.LoginView):
    template_name = "users/login.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Login | Blogthedata.com"
        context["description"] = "Login to your account"
        return context


class MyLogoutView(auth_views.LogoutView):
    template_name = "users/logout.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Logout | Blogthedata.com"
        context["description"] = "Logout of your account"
        return context


class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password | Blogthedata.com"
        context["description"] = "Reset your password"
        return context


class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password Email Sent | Blogthedata.com"
        context["description"] = "Your password reset email has been sent!"
        return context


class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password Confirm | Blogthedata.com"
        context["description"] = "Are you sure you want to reset your password?"
        return context


class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password Complete | Blogthedata.com"
        context["description"] = "Your password has been reset!"
        return context
