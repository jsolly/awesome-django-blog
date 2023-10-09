from django import setup
from dotenv import load_dotenv
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings.ci"
setup()

load_dotenv()

from django.test import TestCase
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User

# Local imports
from blog.models import Post, Category
from .utils import create_unique_post, create_comment


class SetUp(TestCase):
    setup_test_environment()

    @classmethod
    def setUpTestData(cls):
        cls.test_password = "admin"
        cls.default_category = Category.objects.get(slug="uncategorized")
        cls.admin_user = User.objects.get(username="admin")
        cls.comment_only_user = User.objects.get_or_create(
            username="comment_only",
            email="comment_only@example.com",
            password=cls.test_password,
        )[0]
        cls.first_post = create_unique_post()
        cls.first_comment = create_comment(cls.first_post)
        cls.draft_post = create_unique_post(draft=True)

    def tearDown(self):
        Post.objects.all().delete()
