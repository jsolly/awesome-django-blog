from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from blog.models import Category


def RegisterView(request):
    cat_list = Category.objects.all()
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            secret_password = form.cleaned_data.get("secret_password")
            if secret_password != "African Swallows":
                human = False
                messages.error(request, "Hmm, I don't think that is the right password")
            else:
                human = True
                form.save()
                username = form.cleaned_data.get("username")
                messages.success(request, f"Account created for {username}")
                return redirect("login")

    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form, "cat_list":cat_list})


@login_required
def ProfileView(request):
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