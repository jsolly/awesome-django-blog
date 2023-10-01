from django.shortcuts import redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy


class RegisterView(FormView):
    form_class = UserRegisterForm
    success_url = reverse_lazy("login")
    template_name = "users/register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Register | Blogthedata.com"
        context[
            "description"
        ] = "Register for an account on blogthedata.com. It's free!"
        return context

    def form_valid(self, form):
        secret_password = form.cleaned_data.get("secret_password")
        if secret_password != "African Swallows":
            messages.error(
                self.request, "Hmm, I don't think that is the right password"
            )
            return self.form_invalid(form)
        else:
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(self.request, f"Account created for {username}!")
            return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class ProfileView(TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["u_form"] = UserUpdateForm(instance=self.request.user)
        context["p_form"] = ProfileUpdateForm(instance=self.request.user.profile)
        context["title"] = "Profile | Blogthedata.com"
        context["description"] = "Update your profile information on Blogthedata.com"
        return context

    def post(self, request, *args, **kwargs):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated. Thanks!")
            return redirect("profile")

        return self.render_to_response(self.get_context_data())


class MyLoginView(auth_views.LoginView):
    template_name = "users/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Login | Blogthedata.com"
        context[
            "description"
        ] = "Login to your account on blogthedata.com to access your profile and more!"
        return context


class MyLogoutView(auth_views.LogoutView):
    template_name = "users/logout.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Logout | Blogthedata.com"
        context["description"] = "Logout of your account on blogthedata.com"
        return context


class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password | Blogthedata.com"
        context["description"] = "Reset your password on blogthedata.com"
        return context


class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password Email Sent | Blogthedata.com"
        context[
            "description"
        ] = "Your password reset email for blogthedata.com has been sent!"
        return context


class MyPasswordResetConfirmView(
    auth_views.PasswordResetConfirmView
):  # pragma: no cover
    template_name = "users/password_reset_confirm.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password Confirm | Blogthedata.com"
        context[
            "description"
        ] = "Are you sure you want to reset your password for blogthedata.com?"
        return context


class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = "Reset Password Complete | Blogthedata.com"
        context["description"] = "Your password has been reset for blogthedata.com!"
        return context
