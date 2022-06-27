from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from blog.utils import slugify_instance_title
from siteanalytics.utils import get_IP_details
import os


class TestUtils(SetUp, MiddlewareMixin):
    """Tests for helper functions"""

    def test_slugify_instance_title(self):
        slugify_instance_title(self.post1, new_slug="My-First-Post", save=True)
        self.assertEqual(self.post1.slug, "My-First-Post")

    def test_get_IP_details(self):
        access_token = os.environ["IP_INFO_TOKEN"]
        ip_addr = "156.74.181.208"
        details = get_IP_details(ip_addr, access_token)
        self.assertEqual(details.city, "Seattle")
