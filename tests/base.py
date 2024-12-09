from django import setup
from dotenv import load_dotenv
import os

os.environ["USE_SQLITE"] = "True"
os.environ["USE_CLOUD"] = "False"
# Set the site id to 1 because we need to create a site object in the database
os.environ["SITE_ID"] = "1"
setup()

load_dotenv()

from django.test import TestCase
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test.client import Client

# Local imports
from blog.models import Post, Category
from .utils import create_unique_post, create_comment


class SetUp(TestCase):
    setup_test_environment()
    Site.objects.get_or_create(domain='testserver', defaults={'name': 'Test Server'})
    Site.objects.get_or_create(domain='www.testserver', defaults={'name': 'WWW Test Server'})

    @classmethod
    def setUpTestData(cls):
        cls.admin_user_password = "admin"
        cls.comment_only_user_password = "comment_only"
        cls.default_category = Category.objects.get(slug="uncategorized")
        cls.admin_user = User.objects.get(username="admin")
        cls.comment_only_user = User.objects.get(username="comment_only")
        cls.first_post = create_unique_post()
        cls.first_comment = create_comment(cls.first_post)
        cls.draft_post = create_unique_post(draft=True)
        # Create a client that follows redirects
        cls.client = Client(follow=True)

    def tearDown(self):
        Post.objects.all().delete()
