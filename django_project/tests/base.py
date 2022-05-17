import warnings

from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.test.utils import setup_test_environment
from blog.models import Post, Comment, Category, IpPerson
from users.models import User, Profile


def message_in_response(response, message: str):
    for resp_message in get_messages(response.wsgi_request):
        if message == resp_message.message:
            return True
    return False


def create_several_posts(category_name, user, number_of_posts):
    for i in range(number_of_posts):
        Post.objects.create(
            title="My First Post",
            slug=f"{i}",
            category=category_name,
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
        warnings.simplefilter("ignore", category=ResourceWarning)
        self.localhost_ip = "127.0.0.1"

        if IpPerson.objects.filter(ip=self.localhost_ip).exists():
            localhost_ip_person = IpPerson.objects.get(ip=self.localhost_ip)
            localhost_ip_person.delete()

        # SuperUser Object
        self.super_user = User(username="John_Solly", email="test@original.com")
        self.super_user_password = "T3stingIsFun!"
        self.super_user.is_staff = True
        self.super_user.is_superuser = True
        self.super_user.set_password(self.super_user_password)
        self.super_user.save()
        self.profile1 = Profile.objects.get(user=self.super_user)

        # Basic User
        self.basic_user = User(username="test_viewer", email="test@original.com")
        self.basic_user_password = "T3stingIsFun!"
        self.basic_user.is_staff = False
        self.basic_user.is_superuser = False
        self.basic_user.set_password(self.super_user_password)
        self.basic_user.save()
        self.profile2 = Profile.objects.get(user=self.basic_user)

        # Post Object
        self.category1 = Category.objects.create(name="TEST")
        self.post1 = Post.objects.create(
            title="My First Post",
            slug="first-post",
            category=self.category1.name,
            metadesc="Curious about your health? Look no further!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.super_user
            # likes
            # views
        )

        # draft post
        self.draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            category=self.category1.name,
            metadesc="Curious about your health? Look no further!",
            draft=True,
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            author=self.super_user,
        )
        self.post1_like_url = reverse("post-like", args=[self.post1.slug])
        self.post1_detail_url = reverse("post-detail", args=[self.post1.slug])
        self.comment1 = Comment.objects.create(
            post=self.post1, content="I am a comment", author=self.super_user
        )
        self.client = Client()
        self.user_posts_url = reverse("user-posts", args=[self.super_user.username])
        self.post1_update_url = reverse("post-update", args=[self.post1.slug])
        self.post1_delete_url = reverse("post-delete", args=[self.post1.slug])
        self.post1_create_comment_url = reverse(
            "comment-create", args=[self.post1.slug]
        )

        # Users/Admin urls
        # self.password_reset_url = reverse("password_reset")
        # self.password_reset_done_url = reverse("password_reset_done")
        # self.password_reset_confirm = reverse("password_reset_confirm")
        # self.password_reset_complete = reverse("password_reset_complete")
        # self.captcha = reverse("captcha")


# if __name__ == "__main__":
#     unittest.main()
