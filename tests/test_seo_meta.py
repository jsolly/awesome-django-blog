import json
import re

from django.templatetags.static import static

from .base import SetUp


def _canonical_hrefs(html):
    """All canonical hrefs, order-agnostic (django-htmlmin reorders attributes)."""
    tags = re.findall(r'<link\b[^>]*\brel="canonical"[^>]*>', html)
    return [re.search(r'href="([^"]+)"', t).group(1) for t in tags]


def _meta_content(html, attr, value):
    """The content of the <meta> tag whose `attr`="value", or None."""
    for tag in re.findall(r"<meta\b[^>]*>", html):
        if f'{attr}="{value}"' in tag:
            m = re.search(r'content="([^"]*)"', tag)
            return m.group(1) if m else None
    return None


class SeoMetaTests(SetUp):
    """Locks in the SEO head fixes: clean canonical, un-prefixed social image,
    a single canonical on /all-posts/, and valid JSON-LD on post pages."""

    def test_homepage_canonical_points_at_root_with_trailing_slash(self):
        html = self.client.get("/").content.decode()
        self.assertEqual(_canonical_hrefs(html), ["http://testserver/"])

    def test_default_social_image_is_the_bare_static_url(self):
        # Regression: the default og/twitter image must be exactly the static
        # URL. The old code prepended scheme://host, which double-prefixed the
        # already-absolute CloudFront URL in production.
        html = self.client.get("/").content.decode()
        expected = static("iPhoneblogthedata.webp")
        self.assertEqual(_meta_content(html, "property", "og:image"), expected)
        self.assertEqual(_meta_content(html, "name", "twitter:image"), expected)

    def test_all_posts_page_has_exactly_one_self_canonical(self):
        # Regression: all_posts.html used to add a second (homepage) canonical on
        # top of base.html's, leaving the page with two conflicting canonicals.
        html = self.client.get("/all-posts/").content.decode()
        self.assertEqual(_canonical_hrefs(html), ["http://testserver/all-posts/"])

    def test_post_detail_emits_valid_blogposting_and_breadcrumb_jsonld(self):
        html = self.client.get(self.first_post.get_absolute_url()).content.decode()
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
        )
        # json.loads raises (failing the test) if a template comma/escape is wrong.
        parsed = {item["@type"]: item for item in (json.loads(b) for b in blocks)}

        self.assertIn("BlogPosting", parsed)
        self.assertEqual(parsed["BlogPosting"]["headline"], self.first_post.title)
        self.assertEqual(
            parsed["BlogPosting"]["mainEntityOfPage"]["@id"],
            f"http://testserver{self.first_post.get_absolute_url()}",
        )

        crumbs = parsed["BreadcrumbList"]["itemListElement"]
        self.assertEqual([c["position"] for c in crumbs], list(range(1, len(crumbs) + 1)))
        self.assertEqual(crumbs[0]["name"], "Home")
        self.assertEqual(crumbs[-1]["name"], self.first_post.title)
        self.assertTrue(all(c["item"].startswith("http://testserver/") for c in crumbs))
