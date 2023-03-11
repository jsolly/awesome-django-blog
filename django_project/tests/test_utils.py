from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from siteanalytics.utils import get_client_ip, add_visitor_if_not_exist
from blog.utils import create_context, answer_question, load_pickle_file
import pandas as pd
from unittest import mock
from siteanalytics.models import Visitor
from requests.exceptions import HTTPError


class TestUtils(SetUp, MiddlewareMixin):
    # def test_load_data(self):
    #     load_data("django_project/siteanalytics/data/ip_info_test.csv")
    #     self.assertEqual(Visitor.objects.count(), 3)

    def test_load_pickle_file(self):
        df = load_pickle_file()
        self.assertIsInstance(df, pd.DataFrame)

    def test_create_context(self):
        df = load_pickle_file()
        context = create_context(
            "What is the capital of the United States of America?", df
        )
        self.assertIsInstance(context, str)

    @mock.patch("blog.utils.load_pickle_file")
    def test_answer_question(self, mock_load_pickle_file):
        mock_load_pickle_file.return_value = pd.DataFrame(
            {"text": ["The capital of the United States is Washington, D.C."]}
        )

        answer = answer_question(
            question="What is the capital of the United States of America?"
        )
        self.assertEqual(answer, "Washington, D.C.")

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
