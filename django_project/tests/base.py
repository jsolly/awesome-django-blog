import warnings

from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()
from dotenv import load_dotenv

load_dotenv()
from django.test import TestCase, Client
from django.contrib.messages import get_messages
from django.test.utils import setup_test_environment
from blog.models import Post, Category
from users.models import User


def message_in_response(response, message: str):
    for resp_message in get_messages(response.wsgi_request):
        if message == resp_message.message:
            return True
    return False


def create_several_posts(category, user, number_of_posts):
    for i in range(number_of_posts):
        Post.objects.create(
            title="My First Post",
            slug=f"{i}",
            category=category,
            metadesc="Curious about your health? Look no further!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="ultrices dui sapien eget mi proin sed libero enim sed faucibus turpis in eu mi bibendum neque egestas congue quisque egestas diam in arcu cursus euismod quis viverra nibh cras pulvinar mattis nunc sed blandit libero volutpat sed cras ornare arcu dui vivamus arcu felis bibendum ut tristique et egestas",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=user
            # likes
            # views
        )


class SetUp(TestCase):
    """Create User and Post object to be shared by tests. Also create urls using reverse()"""
    setup_test_environment()

    def setUp(self):
        self.general_password = "T3stingIsFun!"
        warnings.simplefilter("ignore", category=ResourceWarning)

        def create_user(provided_username, super_user=False):
            self.provided_username = User(
                username=provided_username, email="test@original.com"
            )
            self.provided_username.set_password(self.general_password)
            if super_user:
                self.provided_username.is_staff = True
                self.provided_username.is_superuser = True

            self.provided_username.save()
            return User.objects.get(username=provided_username)

        self.super_user = create_user("John_Solly", super_user=True)
        self.basic_user = create_user("basic_user", super_user=False)

        # Post Object
        self.category1 = Category.objects.create(name="TEST")
        self.post1 = Post.objects.create(
            title="My First Post",
            slug="first-post",
            category=self.category1,
            metadesc="Curious about your health? Look no further!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.super_user
        )

        # draft post
        self.draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            category=self.category1,
            metadesc="Curious about your health? Look no further!",
            draft=True,
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            author=self.super_user,
        )
        self.client = Client()


# if __name__ == "__main__":
#     unittest.main()
