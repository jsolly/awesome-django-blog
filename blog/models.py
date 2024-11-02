from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField
from django.conf import settings
import os

# import logging
# logger = logging.getLogger("django")


def slugify_instance(instance, save=False, new_slug=None):
    if new_slug:
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


class CommentManager(models.Manager):
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
        upload_to="post_metaimgs",
        default="default.webp",
    )
    metaimg_alt_txt = models.CharField(max_length=500, default="John Solly Headshot")
    metaimg_attribution = models.CharField(max_length=500, blank=True, null=True)
    content = CKEditor5Field(blank=True, null=True)
    snippet = CKEditor5Field(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = PostManager()  # Make sure objects only include active (not draft) posts.

    def get_related_posts(self) -> models.QuerySet:
        """
        Get the top 3 related posts based on the similarities
        """

        return Post.objects.filter(
            id__in=self.similarities1.order_by("-score").values_list(
                "post2", flat=True
            )[:3]
        )

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance(self, save=False)

        super().save(*args, **kwargs)


class Similarity(models.Model):
    post1 = models.ForeignKey(
        Post, related_name="similarities1", on_delete=models.CASCADE
    )
    post2 = models.ForeignKey(
        Post, related_name="similarities2", on_delete=models.CASCADE
    )
    score = models.FloatField()

    # Ensure that the same pair of posts can't be added twice
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post1", "post2"], name="unique_pair")
        ]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = CKEditor5Field(blank=True, null=True, config_name="extends")
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = CommentManager()

    class Meta:
        ordering = ["date_posted"]

    def __str__(self):
        return f"Comment '{self.content}' by {self.author}"

    def get_absolute_url(self):
        post_url = reverse("post-detail", kwargs={"slug": self.post.slug})
        comments_section_url = f"{post_url}#comments"
        return comments_section_url
