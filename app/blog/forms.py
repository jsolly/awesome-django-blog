from django import forms
from .models import Post, Category, Comment
from .validators import snippet_validator
from django_ckeditor_5.widgets import CKEditor5Widget


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
            "category": forms.Select(),
            "metadesc": forms.TextInput(),
            "metaimg_alt_txt": forms.TextInput(),
            "metaimg_attribution": forms.TextInput(),
            "content": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "snippet": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields["category"].choices = Category.objects.all().values_list(
            "id", "name"
        )
        self.fields["snippet"].validators.append(snippet_validator)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Leave your thoughts here..."}
            )
        }
        labels = {"content": ""}
