from .base import SetUp
from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from django_project.sitemaps import (
    HomeSitemap,
    PostSitemap,
    WorksCitedSiteMap,
)
from .utils import create_post


class TestSitemaps(SetUp):
    def test_home_site_map(self):
        item = HomeSitemap.items(Sitemap)[0]
        self.assertTrue(reverse(item))

    def test_post_site_map(self):
        create_post()
        item = PostSitemap.items(Sitemap)[0]
        self.assertTrue(reverse("post-detail", args=[item.slug]))

    def test_works_cited_site_map(self):
        item = WorksCitedSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(WorksCitedSiteMap.location(Sitemap, item))

    def test_privacy_policy_site_map(self):
        item = WorksCitedSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(WorksCitedSiteMap.location(Sitemap, item))

    def test_category_site_map(self):
        item = WorksCitedSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(reverse("blog-category", args=[item]))

    def test_status_page_site_map(self):
        item = WorksCitedSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(WorksCitedSiteMap.location(Sitemap, item))
