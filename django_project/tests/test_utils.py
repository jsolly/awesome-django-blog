from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from blog.utils import slugify_instance_title
from siteanalytics.utils import load_data, get_client_ip, add_visitor_if_not_exist
from siteanalytics.models import Visitor


class TestUtils(SetUp, MiddlewareMixin):
    """Tests for helper functions"""

    def test_slugify_instance_title(self):
        slugify_instance_title(self.post1, new_slug="My-First-Post", save=True)
        self.assertEqual(self.post1.slug, "My-First-Post")

    # def test_load_data(self):
    #     load_data("django_project/siteanalytics/data/ip_info_test.csv")
    #     self.assertEqual(Visitor.objects.count(), 3)

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

    # def test_add_visitor_if_not_exist_valid(self):
    #     request = HttpRequest()
    #     request.META["REMOTE_ADDR"] = "185.7.145.88"
    #     self.assertIsInstance(add_visitor_if_not_exist(request), Visitor)

    # def test_add_visitor_if_not_exist_invalid(self):
    #     request = HttpRequest()
    #     request.META["REMOTE_ADDR"] = "hordor.hordor.hordor.hordor"
    #     self.assertFalse(add_visitor_if_not_exist(request))
    #     request.META["REMOTE_ADDR"] = "127.0.0.1"
    #     self.assertFalse(add_visitor_if_not_exist(request))

    # def test_add_visitor_if_not_exist_already_exisits(self):
    #     request = HttpRequest()
    #     request.META["REMOTE_ADDR"] = "180.151.107.213"  # This is in ip_info_test.csv
    #     self.assertFalse(add_visitor_if_not_exist(request))
