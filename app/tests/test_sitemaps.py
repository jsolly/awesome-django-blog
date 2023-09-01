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
from .utils import create_post


class TestSitemaps(SetUp):
    def test_home_site_map(self):
        item = HomeSitemap.items(Sitemap)[0]
        self.assertTrue(reverse(item))

    def test_post_site_map(self):
        post = create_post()
        sitemap = PostSitemap()
        item = sitemap.items()[0]
        self.assertEqual(sitemap.lastmod(item), post.date_posted)
        self.assertTrue(reverse("post-detail", args=[item.slug]))

    def test_category_site_map(self):
        item = CategorySitemap.items(Sitemap)[0]
        self.assertTrue(reverse("blog-category", args=[item.slug]))

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
