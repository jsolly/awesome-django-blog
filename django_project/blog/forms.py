from django import forms
from .models import Post, Comment, Category

# choices = [
#     ("software development", "software development"),
#     ("life optimization", "life optimization"),
#     ("shower thoughts", "shower thoughts"),
# ]
choices = Category.objects.all().values_list('name', 'name') # comment this if doing an initial DB migration or changing databases

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "slug", "category", "metadesc", "draft", "metaimg", "content", "snippet",)

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(choices=choices, attrs={"class": "form-control"}),
            "metadesc": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
            "snippet": forms.Textarea(attrs={"class": "form-control"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)

        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control"}),
        }
