from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from blog.utils import slugify_instance_title
from siteanalytics.utils import load_data
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
