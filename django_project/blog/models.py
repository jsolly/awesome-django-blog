from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import filetype
from .utils import slugify_instance_title

class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        return super().filter(draft=False).order_by('-date_posted')

    def all(self, *args, **kwargs):
        return super().order_by('-date_posted')


class Category(models.Model):
    """A category contains a subset of posts that are associated with a single category"""
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=140)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog-category", kwargs={"cat": self.name})


class IpPerson(models.Model):  # Anonymous user
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip


class Post(models.Model):
    """Contains all the information that is relevant to a blog post"""
    title = models.CharField(max_length=60)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.CharField(max_length=100, default='uncategorized')
    metadesc = models.CharField(max_length=140, blank=True, null=True)
    draft = models.BooleanField(default=False)
    metaimg = models.ImageField(default="jsolly.jpeg", upload_to="post_metaimgs/")
    metaimg_mimetype = models.CharField(max_length=20, default="image/jpeg")
    snippet = RichTextField(max_length=300, blank=True, null=True)
    content = RichTextUploadingField(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(
        IpPerson, related_name="post_likes", blank=True)
    views = models.ManyToManyField(
        IpPerson, related_name="post_views", blank=True)

    objects = PostManager()  # Make sure objects only include active (not draft) posts.

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def total_likes(self):
        return self.likes.count()

    def total_views(self):
        return self.views.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance_title(self, save=False)
        try:
            self.metaimg_mimetype = filetype.guess(self.metaimg).MIME
        except AttributeError:
            pass

        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    content = RichTextField(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.content)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.post.slug})
