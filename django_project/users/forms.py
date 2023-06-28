from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from captcha.fields import CaptchaField
from django.contrib.auth import (
    password_validation,
)
from django.utils.translation import gettext_lazy as _


class UserRegisterForm(UserCreationForm):
    # email = forms.EmailField()
    # first_name = forms.CharField(max_length=50)
    # last_name = forms.CharField(max_length=50)
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
    secret_password = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "DM me on Twitter (@_jsolly) for the secret password!",
            }
        )
    )
    captcha = CaptchaField()

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"autofocus": True}),
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
            "email": forms.EmailInput(),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]
