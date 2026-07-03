from django.contrib.sitemaps import Sitemap
from blog.models import Post, Category
from django.urls import reverse


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.active()

    def lastmod(self, obj):
        return obj.date_updated

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # order_by keeps sitemap pagination deterministic and silences Django's
        # UnorderedObjectListWarning (Category has no Meta.ordering).
        return Category.objects.all().order_by("name")

    def location(self, obj):
        return obj.get_absolute_url()


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.3

    def items(self):
        return [
            'home',
            'works-cited',
            'privacy',
            'status',
            'all-posts',
        ]

    def location(self, item):
        return reverse(item)
