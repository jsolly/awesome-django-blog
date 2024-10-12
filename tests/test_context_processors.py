from .base import SetUp
from django.urls import reverse, resolve
from blog.context_processors import category_renderer, breadcrumbs
from django.test.client import RequestFactory


class TestContextProcessors(SetUp):
    def setUp(self):
        self.factory = RequestFactory()

    def test_category_renderer(self):
        path = reverse("blog-category", args=["uncategorized"])
        request = self.factory.get(path)
        request.resolver_match = resolve(path)
        result = category_renderer(request)
        self.assertEqual(result["current_category"], "uncategorized")
        self.assertEqual(len(result["category_qs"]), 1)
        self.assertEqual(result["category_qs"][0].name, "Uncategorized")

    def test_home_breadcrumb(self):
        request = self.factory.get("/")
        result = breadcrumbs(request)
        self.assertEqual(len(result["breadcrumbs"]), 1)
        self.assertEqual(result["breadcrumbs"][0]["name"], "Home")
        self.assertEqual(result["breadcrumbs"][0]["url"], reverse("home"))

    def test_blog_category_breadcrumb(self):
        request = self.factory.get(reverse("blog-category", args=["uncategorized"]))
        result = breadcrumbs(request)
        self.assertEqual(len(result["breadcrumbs"]), 2)
        self.assertEqual(result["breadcrumbs"][1]["name"], "Uncategorized")
        self.assertEqual(
            result["breadcrumbs"][1]["url"],
            reverse("blog-category", args=["uncategorized"]),
        )

    def test_post_detail_breadcrumb(self):
        request = self.factory.get(reverse("post-detail", args=[self.first_post.slug]))
        result = breadcrumbs(request)
        self.assertEqual(len(result["breadcrumbs"]), 3)
        self.assertEqual(
            result["breadcrumbs"][1]["name"], self.first_post.category.name
        )
        self.assertEqual(
            result["breadcrumbs"][1]["url"],
            reverse("blog-category", args=[self.first_post.category.slug]),
        )
        self.assertEqual(result["breadcrumbs"][2]["name"], self.first_post.title)
        self.assertEqual(
            result["breadcrumbs"][2]["url"],
            reverse("post-detail", args=[self.first_post.slug]),
        )

    def test_works_cited_breadcrumb(self):
        request = self.factory.get(reverse("works-cited"))
        result = breadcrumbs(request)
        self.assertEqual(len(result["breadcrumbs"]), 2)
        self.assertEqual(result["breadcrumbs"][1]["name"], "Works Cited")
        self.assertEqual(result["breadcrumbs"][1]["url"], reverse("works-cited"))

    def test_privacy_breadcrumb(self):
        request = self.factory.get(reverse("privacy"))
        result = breadcrumbs(request)
        self.assertEqual(len(result["breadcrumbs"]), 2)
        self.assertEqual(result["breadcrumbs"][1]["name"], "Privacy Policy")
        self.assertEqual(result["breadcrumbs"][1]["url"], reverse("privacy"))

    def test_invalid_url_breadcrumb(self):
        request = self.factory.get("/invalid-url/")
        result = breadcrumbs(request)
        self.assertEqual(len(result["breadcrumbs"]), 0)
