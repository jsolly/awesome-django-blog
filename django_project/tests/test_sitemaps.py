from .base import SetUp
from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from django_project.sitemaps import RoadmapSitemap


class TestModels(SetUp):
    def test_road_site_map(self):
        item = RoadmapSitemap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(RoadmapSitemap.location(Sitemap, item))
