from django import forms
from .models import Post, Category, Comment


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
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields["category"].choices = Category.objects.all().values_list(
            "id", "name"
        )


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
