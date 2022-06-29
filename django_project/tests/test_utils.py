from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from blog.utils import slugify_instance_title
from siteanalytics.utils import load_data, get_client_ip
from siteanalytics.models import Visitor
import pytest


class TestUtils(SetUp, MiddlewareMixin):
    """Tests for helper functions"""

    def test_slugify_instance_title(self):
        slugify_instance_title(self.post1, new_slug="My-First-Post", save=True)
        self.assertEqual(self.post1.slug, "My-First-Post")

    @pytest.mark.skip(reason="Need to use test fixtures before this will pass")
    def test_load_data(self):
        load_data("django_project/siteanalytics/data/ip_info_small.csv")
        self.assertEqual(Visitor.objects.count(), 5)

    def test_get_client_ip_CF(self):
        request = HttpRequest()
        request.META["HTTP_CF_CONNECTING_IP"] = "185.7.145.88"
        self.assertEqual(get_client_ip(request), "185.7.145.88")

    def test_get_client_ip_X_FORWARD(self):
        request = HttpRequest()
        request.META["HTTP_X_FORWARD_FOR"] = "185.7.145.88,0"
        self.assertEqual(get_client_ip(request), "185.7.145.88")

    def test_get_client_ip_REMOTE_ADDR(self):
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "185.7.145.88"
        self.assertEqual(get_client_ip(request), "185.7.145.88")
