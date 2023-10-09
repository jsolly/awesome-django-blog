from .base import SetUp
from django.urls import reverse
from django.contrib.sitemaps import Sitemap

from app.sitemaps import (
    HomeSitemap,
    PostSitemap,
    CategorySitemap,
    WorksCitedSiteMap,
    privacyPolicySiteMap,
    PortfolioSiteMap,
    StatusPageSiteMap,
)
from blog.models import Post


class TestSitemaps(SetUp):
    def test_home_site_map(self):
        return True
        item = HomeSitemap.items(Sitemap)[0]
        self.assertTrue(reverse(item))

    def test_post_site_map(self):
        sitemap = PostSitemap()
        item = sitemap.items()[0]
        self.assertTrue(reverse("post-detail", args=[item.slug]))
        self.assertTrue(sitemap.location(item))

    def test_category_site_map(self):
        item = CategorySitemap.items(Sitemap)[0]
        self.assertTrue(reverse("blog-category", args=[item.slug]))
        self.assertTrue(CategorySitemap.location(Sitemap, item))

    def test_works_cited_site_map(self):
        item = WorksCitedSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(WorksCitedSiteMap.location(Sitemap, item))

    def test_privacy_policy_site_map(self):
        item = privacyPolicySiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(privacyPolicySiteMap.location(Sitemap, item))

    def test_portfolio_site_map(self):
        item = PortfolioSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(PortfolioSiteMap.location(Sitemap, item))

    def test_status_page_site_map(self):
        item = StatusPageSiteMap.items(Sitemap)[0]
        self.assertTrue(reverse(item))
        self.assertTrue(StatusPageSiteMap.location(Sitemap, item))
