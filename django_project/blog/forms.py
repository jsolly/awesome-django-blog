from django import forms
from .models import Post

choices = [
    ("life advice", "life advice"),
    ("site updates", "site updates"),
]
# choices = Category.objects.all().values_list('name', 'name') # comment this if doing an initial DB migration or changing databases
# I don't think I am doing


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
            "content",
            "snippet",
        )

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(choices=choices, attrs={"class": "form-control"}),
            "metadesc": forms.TextInput(attrs={"class": "form-control"}),
        }
