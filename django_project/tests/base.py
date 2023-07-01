import warnings
from django import setup
from dotenv import load_dotenv
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings.ci"
setup()

load_dotenv()

from django.test import TestCase
from django.test.utils import setup_test_environment

# Local imports
from blog.models import Category


class SetUp(TestCase):
    setup_test_environment()

    @classmethod
    def setUpTestData(cls):
        warnings.simplefilter("ignore", category=ResourceWarning)
        cls.test_password = "defaultpassword"
        cls.test_category, _ = Category.objects.get_or_create(name="Test Category")
