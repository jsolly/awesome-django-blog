from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from blog.utils import get_client_ip, slugify_instance_title


class TestUtils(SetUp, MiddlewareMixin):
    """Tests for helper functions"""

    def test_get_client_ip(self):
        request = self.client.get(self.post1_detail_url).wsgi_request
        self.assertEqual(get_client_ip(request), self.localhost_ip)

        # Simulate connecting via proxy server
        request.META["HTTP_X_FORWARD_FOR"] = "1.1.1.1, 127.0.0.1"
        self.assertEqual(get_client_ip(request), "1.1.1.1")

    def test_slugify_instance_title(self):
        slugify_instance_title(self.post1, new_slug="My-First-Post", save=True)
        self.assertEqual(self.post1.slug, "My-First-Post")

    def test_post_like_status(self):
        self.assertFalse(self.post1.likes.filter(ip=self.localhost_ip).exists())
