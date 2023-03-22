from django import forms
from .models import Post
from .models import Category
from django.conf import settings

choices = [
    ("productivity", "productivity"),
    ("geodev", "geodev"),
    ("portfolio", "portfolio"),
    ("resources", "resources"),
    ("webdev", "webdev"),
    ("devtools", "devtools"),
]
if settings.SETTINGS_MODULE in [
    "django_project.settings.dev",
    "django_project.settings.prod",
]:
    choices = Category.objects.all().values_list("name", "name")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "slug",
            "category",
            "metadesc",
            "draft",
            "metaimg",
            "metaimg_alt_txt",
            "metaimg_attribution",
            "content",
            "snippet",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "autofocus": True,
                }
            ),
            "slug": forms.TextInput(),
            "category": forms.Select(choices=choices),
            "metadesc": forms.TextInput(),
            "metaimg_alt_txt": forms.TextInput(),
            "metaimg_attribution": forms.TextInput(),
        }
