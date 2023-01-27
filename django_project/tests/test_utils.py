from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from blog.utils import slugify_instance_title
from siteanalytics.utils import get_client_ip
from unittest import mock
from siteanalytics.utils import add_visitor_if_not_exist
from siteanalytics.models import Visitor
from requests.exceptions import HTTPError


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

    @mock.patch("siteanalytics.utils.ipinfo")
    def test_add_visitor_if_not_exist_valid(self, mock_ipinfo):
        # Set up the mock object for the ipinfo library
        mock_ipinfo.getHandler.return_value.getDetails.return_value.ip = "185.7.145.88"
        mock_ipinfo.getHandler.return_value.getDetails.return_value.country = "US"
        mock_ipinfo.getHandler.return_value.getDetails.return_value.city = "New York"
        mock_ipinfo.getHandler.return_value.getDetails.return_value.longitude = (
            "40.730610"
        )
        mock_ipinfo.getHandler.return_value.getDetails.return_value.latitude = (
            "-73.935242"
        )

        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "185.7.145.88"
        self.assertIsInstance(add_visitor_if_not_exist(request), Visitor)

    @mock.patch("siteanalytics.utils.ipinfo.getHandler")
    def test_add_visitor_if_not_exist_invalid(self, mock_get_handler):
        mock_handler = mock.MagicMock()
        mock_get_handler.return_value = mock_handler
        mock_handler.getDetails.side_effect = HTTPError

        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "0.0.0.0"
        self.assertFalse(add_visitor_if_not_exist(request))
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        self.assertFalse(add_visitor_if_not_exist(request))

    @mock.patch("siteanalytics.utils.Visitor.objects.get")
    def test_add_visitor_if_already_exists(self, mock_visitor_get):
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = "180.151.107.213"  # This is in ip_info_test.csv

        # Set up the mock to return a Visitor object
        mock_visitor = mock.MagicMock()
        mock_visitor_get.return_value = mock_visitor

        # Call the function and assert that it returns None
        self.assertIsNone(add_visitor_if_not_exist(request))
        # Assert that Visitor.objects.get was called with the correct IP address
        mock_visitor_get.assert_called_with(ip_addr="180.151.107.213")
