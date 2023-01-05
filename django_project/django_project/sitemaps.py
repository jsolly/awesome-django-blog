from django.contrib.sitemaps import Sitemap
from blog.models import Post, Category
from django.urls import reverse


class HomeSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ["home"]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.date_posted

    # def location() Django uses get_absolute_url() by default

class WorksCitedSiteMap(Sitemap):
    changefreq = "monthly"
    priority = 0.1

    def items(self):
        return ["works-cited"]

    def location(self, item):
        return reverse(item)
