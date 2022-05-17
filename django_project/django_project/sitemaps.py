from django.contrib.sitemaps import Sitemap
from blog.models import Post
from django.urls import reverse


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.date_posted

    # def location() Django uses get_absolute_url() by defaultsss


class RoadmapSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return ["blog-roadmap"]

    def location(self, item):
        return reverse(item)