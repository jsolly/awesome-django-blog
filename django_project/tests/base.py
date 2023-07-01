import warnings
from django import setup
from dotenv import load_dotenv
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings.ci"
setup()

load_dotenv()

from django.test import TestCase, Client
from django.test.utils import setup_test_environment

# Local imports
from blog.models import Category


class SetUp(TestCase):
    setup_test_environment()

    def setUp(self):
        warnings.simplefilter("ignore", category=ResourceWarning)
        self.client = Client()
        self.test_password = "defaultpassword"
        if len(Category.objects.all()) == 0:
            self.test_category = Category.objects.create(name="Test Category")
        else:
            self.test_category = Category.objects.all()[0]
