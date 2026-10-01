from django.test import Client, override_settings

from .base import SetUp


@override_settings(ALLOWED_HOSTS=["www.blogthedata.com", "blogthedata.com"])
class CanonicalResponseTests(SetUp):
    def test_public_page_and_missing_page_preserve_statuses(self):
        client = Client()
        page = client.get("/", HTTP_HOST="www.blogthedata.com", secure=True)
        missing = client.get("/missing-page/", HTTP_HOST="www.blogthedata.com", secure=True)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(missing.status_code, 404)
        self.assertNotIn("x-release-id", page)

    def test_noncanonical_host_redirect_preserves_path_and_query(self):
        response = Client().get(
            "/all-posts/?page=2", HTTP_HOST="blogthedata.com", secure=True
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://www.blogthedata.com/all-posts/?page=2")
