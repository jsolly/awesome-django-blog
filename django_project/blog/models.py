from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from .utils import slugify_instance_title

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog-home")

class IpPerson(models.Model): #Anonymous user
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, default='uncategorized')
    likes = models.ManyToManyField(IpPerson, related_name="post_likes", blank=True)
    views = models.ManyToManyField(IpPerson, related_name="post_views", blank=True)

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
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = RichTextField(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.post.slug})
