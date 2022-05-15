from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from blog.models import Category


def register_view(request):
    cat_list = Category.objects.all()
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

    return render(request, "users/register.html", {"form": form, "cat_list": cat_list})


@login_required
def profile_view(request):
    cat_list = Category.objects.all()
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

    context = {"u_form": u_form, "p_form": p_form, "cat_list": cat_list}
    return render(request, "users/profile.html", context=context)


class MyLoginView(auth_views.LoginView):
    template_name = "users/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class MyLogoutView(auth_views.LogoutView):
    template_name = "users/logout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context
