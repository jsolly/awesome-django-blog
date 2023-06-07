from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
import logging
from django_resized import ResizedImageField

logger = logging.getLogger("django")

# def post_pre_save(sender, instance, *args, **kwargs):
#     print("pre_save")
#     if instance.slug is None:
#         slugify_instance_title(instance)

# pre_save.connect(post_pre_save, sender=Post)

# def post_post_save(sender, instance, created, *args, **kwargs):
#     print("post_save")
#     if created:
#         slugify_instance_title(instance, save=True)

# post_save.connect(post_post_save, sender=Post)


def slugify_instance(instance, save=False, new_slug=None):
    if new_slug is not None:
        instance.slug = new_slug
    else:
        if isinstance(instance, Post):
            instance.slug = slugify(instance.title)
        elif isinstance(instance, Category):
            instance.slug = slugify(instance.name)

    if save:
        instance.save()


class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        return super().filter(draft=False).order_by("-date_posted")

    def all(self, *args, **kwargs):
        return super().order_by("-date_posted")


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.CharField(max_length=140)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog-category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance(self, save=False)

        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    metadesc = models.CharField(max_length=500, blank=True, null=True)
    draft = models.BooleanField(default=False)
    metaimg = ResizedImageField(
        force_format="WEBP",
        quality=75,
        upload_to="post_metaimgs/",
        default="jsolly.webp",
    )
    metaimg_alt_txt = models.CharField(max_length=500, default="John Solly Headshot")
    metaimg_attribution = models.CharField(max_length=500, blank=True, null=True)
    content = CKEditor5Field(blank=True, null=True, config_name="extends")
    snippet = CKEditor5Field(blank=True, null=True, config_name="extends")
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = PostManager()  # Make sure objects only include active (not draft) posts.

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance(self, save=False)

        super().save(*args, **kwargs)

# POST COMMENT MODEL
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_posted"]

    def __str__(self):
        return "Comment {} by {}".format(self.author, self.title)