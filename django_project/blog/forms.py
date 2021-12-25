from django import forms
from .models import Post, Comment, Category

my_choices = list(Category.objects.all().values_list('name', 'name'))
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "category", "content")

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(choices=my_choices, attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)

        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control"}),
        }
