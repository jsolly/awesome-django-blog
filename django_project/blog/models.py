from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
import filetype
from .utils import slugify_instance_title


class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        return super().filter(draft=False).order_by("-date_posted")

    def all(self, *args, **kwargs):
        return super().order_by("-date_posted")


class Category(models.Model):
    """A category contains a subset of posts that are associated with a single category"""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=140)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog-category", kwargs={"category": self.name})


class Post(models.Model):
    """Contains all the information that is relevant to a blog post"""

    title = models.CharField(max_length=110)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    metadesc = models.CharField(max_length=140, blank=True, null=True)
    draft = models.BooleanField(default=False)
    metaimg = models.ImageField(default="jsolly.jpeg", upload_to="post_metaimgs/")
    metaimg_mimetype = models.CharField(max_length=20, default="image/jpeg")
    metaimg_alt_txt = models.CharField(max_length=120, default="Meta Image")
    content = CKEditor5Field(blank=True, null=True, config_name="extends")
    snippet = CKEditor5Field(blank=True, null=True, config_name="extends")
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = PostManager()  # Make sure objects only include active (not draft) posts..

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance_title(self, save=False)
        try:
            self.metaimg_mimetype = filetype.guess(self.metaimg.path).MIME
        except AttributeError:
            pass

        super().save(*args, **kwargs)
