from .base import SetUp
from django.test import override_settings
from unittest.mock import patch


class testMiddleware(SetUp):
    @override_settings(SETTINGS_MODULE="django_project.settings.prod")
    @patch("siteanalytics.utils.add_visitor_if_not_exist")
    def test_request_track_middleware(self, mock_add_visitor):
        self.client.get("/")
