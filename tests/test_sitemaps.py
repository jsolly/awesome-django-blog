from .base import SetUp
from django.urls import reverse

from app.sitemaps import (
    StaticSitemap,
    PostSitemap,
    CategorySitemap,
)
from blog.models import Category
from .utils import create_unique_post


class TestSitemaps(SetUp):
    def test_post_sitemap(self):
        sitemap = PostSitemap()
        item = sitemap.items()[0]
        self.assertTrue(reverse("post-detail", args=[item.slug]))
        self.assertTrue(sitemap.location(item))
        self.assertEqual(sitemap.changefreq, "weekly")
        self.assertEqual(sitemap.priority, 0.8)
        self.assertEqual(sitemap.lastmod(item), item.date_updated)

    def test_category_sitemap(self):
        sitemap = CategorySitemap()
        item = sitemap.items()[0]
        self.assertTrue(reverse("blog-category", args=[item.slug]))
        self.assertTrue(sitemap.location(item))
        self.assertEqual(sitemap.changefreq, "weekly")
        self.assertEqual(sitemap.priority, 0.6)

    def test_category_sitemap_excludes_empty_and_draft_only(self):
        filled = Category.objects.create(
            name="Filled", slug="filled", description="Has a public post"
        )
        Category.objects.create(name="Empty", slug="empty-cat", description="No posts")
        Category.objects.create(
            name="Drafts Only", slug="draft-only", description="Drafts only"
        )
        create_unique_post(category="filled")
        create_unique_post(category="draft-only", draft=True)

        slugs = [c.slug for c in CategorySitemap().items()]
        self.assertIn(filled.slug, slugs)
        self.assertNotIn("empty-cat", slugs)
        self.assertNotIn("draft-only", slugs)

        xml = self.client.get(
            reverse("django.contrib.sitemaps.views.sitemap")
        ).content.decode()
        self.assertIn("/category/filled/", xml)
        self.assertNotIn("/category/empty-cat/", xml)
        self.assertNotIn("/category/draft-only/", xml)

    def test_static_sitemap(self):
        sitemap = StaticSitemap()
        items = sitemap.items()

        # Test sitemap configuration
        self.assertEqual(sitemap.changefreq, "monthly")
        self.assertEqual(sitemap.priority, 0.3)

        # Test all static URLs are included
        expected_urls = ["home", "works-cited", "privacy", "status", "all-posts"]
        self.assertEqual(items, expected_urls)

        # Test each URL can be reversed and located
        for item in items:
            self.assertTrue(reverse(item))
            self.assertEqual(sitemap.location(item), reverse(item))
