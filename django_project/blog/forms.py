from django import forms
from .models import Post, Comment, Category

choices = [
    ("software development", "software development"),
    ("life optimization", "life optimization"),
    ("shower thoughts", "shower thoughts"),
]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "category", "content")

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(choices=choices, attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)

        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control"}),
        }
