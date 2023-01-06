from .base import SetUp
from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from django_project.sitemaps import (
    HomeSitemap,
    PostSitemap,
    WorksCitedSiteMap,
)


class TestModels(SetUp):
    def test_home_site_map(self):
        item = HomeSitemap.items(Sitemap)[0]
        self.assertTrue(reverse(item))

    def test_post_site_map(self):
        item = PostSitemap.items(Sitemap)[0]
        self.assertTrue(reverse("post-detail", args=[item.slug]))

    def test_works_cited_site_map(self):
        item = WorksCitedSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(WorksCitedSiteMap.location(Sitemap, item))
