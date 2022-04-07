import os
import unittest
import warnings
from PIL import Image

from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()
from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.contrib.messages import get_messages
from django.test.utils import setup_test_environment
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import views as auth_views
from blog.views import (
    add_ip_person_if_not_exist,
    add_ip_person_view_if_not_exist,
    HomeView,
    UserPostListView,
    CreatePostView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CreateCommentView,
    CategoryView,
    AboutView,
    PostLikeView,
    RoadMapView,
    SearchView,
    UnitTestView
)
from blog.forms import PostForm, CommentForm
from blog.models import Post, Comment, Category, IpPerson
from blog.utils import get_client_ip, slugify_instance_title, get_post_like_status
from users.views import RegisterView, ProfileView
from users.models import User, Profile
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def message_in_response(response, message:str):
        for resp_message in get_messages(response.wsgi_request):
            if message == resp_message.message:
                return True
        return False
    



class SetUp(TestCase):
    """Create User and Post object to be shared by tests. Also create urls using reverse()"""
    setup_test_environment()

    def setUp(self):
        warnings.simplefilter('ignore', category=ResourceWarning)
        self.localhost_ip = '127.0.0.1'

        if IpPerson.objects.filter(ip=self.localhost_ip).exists():
            localhost_ip_person = IpPerson.objects.get(ip=self.localhost_ip)
            localhost_ip_person.delete()

        # SuperUser Object
        self.user1 = User(username="test_superuser", email="test@original.com")
        self.user1_password = "T3stingIsFun!"
        self.user1.is_staff = True
        self.user1.is_superuser = True
        self.user1.set_password(self.user1_password)
        self.user1.save()
        self.profile1 = Profile.objects.get(user=self.user1)

        # Viewer

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
            author=self.user1
            # likes
            # views

        )
        self.post1_like_url = reverse("post-like", args=[self.post1.slug])
        self.post1_detail_url = reverse("post-detail", args=[self.post1.slug])
        self.comment1 = Comment.objects.create(
            post=self.post1, content="I am a comment", author=self.user1)
        self.client = Client()
        self.home_url = reverse('blog-home')
        self.post_create_url = reverse("post-create")
        self.user_posts_url = reverse("user-posts", args=[self.user1.username])
        self.post_update_url = reverse("post-update", args=['some-slug'])
        self.post_delete_url = reverse("post-delete", args=['some-slug'])
        self.create_comment_url = reverse("comment-create", args=['some-slug'])
        self.category_url = reverse(
            "blog-category", args=[self.category1.name])
        self.about_url = reverse("blog-about")
        self.roadmap_url = reverse("blog-roadmap")
        self.search_url = reverse("blog-search")
        self.unittest_url = reverse("blog-unittest")

        # Users/Admin urls
        # self.admin_url = reverse("admin")
        self.register_url = reverse("register")
        self.profile_url = reverse("profile")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        # self.password_reset_url = reverse("password_reset")
        # self.password_reset_done_url = reverse("password_reset_done")
        # self.password_reset_confirm = reverse("password_reset_confirm")
        # self.password_reset_complete = reverse("password_reset_complete")
        # self.captcha = reverse("captcha")


class TestUrls(SetUp):
    """Make sure urls are hooked up to the correct View"""

    def test_home_url_is_resolved(self):
        self.assertEqual(resolve(self.home_url).func.view_class, HomeView)

    def test_user_posts_url_is_resolved(self):
        self.assertEqual(
            resolve(self.user_posts_url).func.view_class, UserPostListView)

    def test_create_post_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post_create_url).func.view_class, CreatePostView)

    def test_post_detail_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post1_detail_url).func.view_class, PostDetailView)

    def test_post_update_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post_update_url).func.view_class, PostUpdateView)

    def test_post_delete_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post_delete_url).func.view_class, PostDeleteView)

    def test_create_comment_url_is_resolved(self):
        self.assertEqual(
            resolve(self.create_comment_url).func.view_class, CreateCommentView)

    def test_category_url_is_resolved(self):
        self.assertEqual(
            resolve(self.category_url).func.view_class, CategoryView)

    def test_about_url_is_resolved(self):
        self.assertEqual(resolve(self.about_url).func, AboutView)

    def test_post_like_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post1_like_url).func, PostLikeView)

    def test_roadmap_url_is_resolved(self):
        self.assertEqual(
            resolve(self.roadmap_url).func, RoadMapView)

    def test_search_url_is_resolved(self):
        self.assertEqual(resolve(self.search_url).func, SearchView)

    def test_unittest_url_is_resolved(self):
        self.assertEqual(
            resolve(self.logout_url).func.view_class, auth_views.LogoutView)

    def test_register_url_is_resolved(self):
        self.assertEqual(resolve(self.register_url).func, RegisterView)

    def test_profile_url_is_resolved(self):
        self.assertEqual(resolve(self.profile_url).func, ProfileView)

    def test_login_url_is_resolved(self):
        self.assertEqual(
            resolve(self.login_url).func.view_class, auth_views.LoginView)
        self.assertEqual(f"/{settings.LOGIN_URL}", self.login_url)

    def test_logout_url_is_resolved(self):
        self.assertEqual(
            resolve(self.logout_url).func.view_class, auth_views.LogoutView)

    # def test_password_reset_url_is_resolved(self):
    #     self.assertEqual(resolve(self.password_reset_url).func.view_class, auth_views.PasswordResetView)

    # def test_password_resset_done_url_is_resolved(self):
    #     self.assertEqual(resolve(self.password_reset_done_url).func.view_class, auth_views.PasswordResetDoneView)

    # def test_password_reset_confirm_url_is_resolved(self):
    #     self.assertEqual(resolve(self.password_reset_confirm).func.view_class, auth_views.PasswordResetConfirmView)

    # def test_password_reset_complete_url_is_resolved(self):
    #     self.assertEqual(resolve(self.password_reset_complete).func.view_class, auth_views.PasswordResetCompleteView)

    # def test_captcha_url_is_resolved(self):
    #     self.assertEqual(resolve(self.logout_url).func.view_class, auth_views.LogoutView)


class TestViews(SetUp, MiddlewareMixin):
    def test_add_ip_person_if_not_exist(self):
        self.assertFalse(IpPerson.objects.filter(
            ip=self.localhost_ip).exists())
        request = self.client.get(self.home_url).wsgi_request
        add_ip_person_if_not_exist(request)
        self.assertTrue(IpPerson.objects.filter(ip=self.localhost_ip).exists())

    def test_add_ip_person_view_if_not_exist(self):
        self.assertFalse(self.post1.views.filter(
            ip=self.localhost_ip).exists())
        request = self.client.get(self.post1_detail_url).wsgi_request

        ip_person = add_ip_person_view_if_not_exist(request, self.post1)
        self.assertTrue(self.post1.views.filter(ip=ip_person.ip).exists())
        self.post1.views.get(ip=self.localhost_ip).delete()

    def test_home_view(self):  # TODO
        # Anonymous user
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/home.html')

        # Access using super_user (should get posts in draft mode)
        self.client.login(username=self.user1.username,
                          password=self.user1_password)
        response = self.client.get(self.home_url)

    def test_user_post_list_view(self):
        response = self.client.get(self.user_posts_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/user_posts.html')

    def test_post_detail_view(self):
        response = self.client.get(self.post1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_create_post_view(self):
        # Admin can create posts
        self.client.login(username=self.user1.username,
                          password=self.user1_password)
        response = self.client.post(self.post_create_url,data=
                                    {
                                        "title": "My Second Post",
                                        "slug": "second-post",
                                        "category": "productivity",
                                        "metadesc": "I can make you more productive!",
                                        "draft": False,
                                        # "metaimg" : ""
                                        # "metaimg"_mimetype : ""
                                        "snippet": "Do the things",
                                        "content": "Do the things. All the things",
                                        # date_posted : ""
                                        "author": self.user1
                                        # "likes"
                                        # "views"

                                    }, follow=True)
        self.assertRedirects(response, expected_url=reverse("post-detail", args=['second-post']))
        self.assertEqual(Post.objects.last().title, "My Second Post")

        # Viewer cannot create posts


    # def test_update_post_view

    # def test_create_comment_view

    # def post_delete_view

    def test_category_view(self):  # TODO
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/categories.html')
        self.assertEqual(response.context['cat'], self.category1.name)

    def test_about_view(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/about.html')
        self.assertIsInstance(response.context['my_profile'], Profile)

    def test_roadmap_view(self):  # TODO
        response = self.client.get(self.roadmap_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/roadmap.html')

    def test_post_like_view(self):
        response = self.client.get(self.post1_like_url, follow=True)
        self.assertRedirects(
            response, expected_url=self.post1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertTrue(self.post1.likes.filter(ip=self.localhost_ip).exists())

        # # Unlike post
        response = self.client.get(self.post1_like_url, follow=True)
        self.assertRedirects(
            response, expected_url=self.post1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertFalse(self.post1.likes.filter(
            ip=self.localhost_ip).exists())

    def test_search_view(self):
        # Empty page if user didn't search for anything and manually typed in the search url (get)
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_posts.html')

        # If anonymous, should be able to find a post
        data = {"searched": "My First Post"}
        response = self.client.post(self.search_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filtered_posts'][0], self.post1)

        # TODO: If authenticated, can see drafts

    def test_unittest_view(self):
        response = self.client.get(self.unittest_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'htmlcov/index.html')

    # Users/Admin Views (also need to re-write)
    # def test_admin_view

    def test_register_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        data = {"username": "test2",
                "email": "example2@test.com",
                "password1": "Coff33cak3s!",
                "password2": "Coff33cak3s!",
                "secret_password": "African Swallows",
                "captcha_0": "dummy-value",
                "captcha_1": "PASSED"}

        response = self.client.post(self.register_url, data=data, follow=True)
        self.assertRedirects(response, expected_url=self.login_url)
        self.assertTemplateUsed(response, 'users/login.html')

        data["secret_password"] = "Wrong Password"
        data["username"] = "test3"

        response = self.client.post(self.register_url, data=data, follow=True)

        self.assertTrue(message_in_response(response, "Hmm, I don't think that is the right password"))

    def test_profile_view(self):
        # View Profile
        self.client.login(username=self.user1.username,
                          password=self.user1_password)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

        # Edit profile
        self.assertEqual(self.user1.email, "test@original.com")
        self.assertEqual(self.user1.username, "test_superuser")
        response = self.client.post(self.profile_url, data={"email": "test@modified.com",
                                    "username": "modified"})
        self.assertTrue(message_in_response(response, "Your account has been updated"))
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, "test@modified.com")
        self.assertEqual(self.user1.username, "modified")
        #TODO Figure out how to change profile photo


class TestUtils(SetUp, MiddlewareMixin):
    """Tests for helper functions"""

    def test_get_client_ip(self):
        request = self.client.get(self.post1_detail_url).wsgi_request
        self.assertEqual(get_client_ip(request), self.localhost_ip)

        # Simulate connecting via proxy server
        request.META['HTTP_X_FORWARD_FOR'] = "1.1.1.1, 127.0.0.1"
        self.assertEqual(get_client_ip(request),
                         '1.1.1.1')

    def test_slugify_instance_title(self):
        slugify_instance_title(self.post1, new_slug='My-First-Post', save=True)
        self.assertEqual(self.post1.slug, 'My-First-Post')

    def test_post_like_status(self):
        self.assertFalse(self.post1.likes.filter(
            ip=self.localhost_ip).exists())


class TestModels(SetUp):
    def test_post_manager_all(self):
        posts = Post.objects.all()
        self.assertIsInstance(posts[0], Post)
        post_count = posts.count()
        Post.objects.create(
            title="My Second Post",
            slug="second-post",
            category="health",
            metadesc="Curious about your health? Look no further!!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.user1
            # likes
            # views

        )
        new_post_count = Post.objects.count()
        self.assertEqual(new_post_count, post_count + 1)

    def test_post_manager_active(self):
        active_posts = Post.objects.active()
        self.assertIsInstance(active_posts[0], Post)
        active_posts_count = active_posts.count()
        post3 = Post.objects.create(
            title="My Second Post",
            slug="second-post",
            category="health",
            metadesc="Curious about your health? Look no further!!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.user1
            # likes
            # views

        )
        new_active_post_count = Post.objects.active().count()
        self.assertEqual(new_active_post_count, active_posts_count + 1)
        post_draft = post3
        # Needed a new variable, else it wasn't saving.
        post_draft.draft = True
        post_draft.save()
        active_posts_minus_draft = Post.objects.active().count()
        self.assertEqual(active_posts_minus_draft, new_active_post_count - 1)

    def test_category(self):
        self.assertIsInstance(Category.objects.all()[0], Category)
        self.assertEqual(self.category1.get_absolute_url(), "/category/TEST/")

    def test_ip_person(self):
        ip_person = IpPerson.objects.create(ip=self.localhost_ip)
        self.assertEqual(str(ip_person), self.localhost_ip)

    def test_post(self):
        self.assertEqual(str(self.post1), "My First Post | test_superuser")
        self.assertEqual(self.post1.get_absolute_url(), "/post/first-post/")

        post_no_slug = Post.objects.create(
            title="No slug given",
            # slug="first-post",
            category="health",
            metadesc="Curious about your health? Look no further!",
            draft=False,
            # metaimg = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            author=self.user1
        )
        self.assertEqual(post_no_slug.slug, "no-slug-given")

    def test_comment(self):
        self.assertEqual(str(self.comment1), "I am a comment")
        self.assertEqual(self.comment1.get_absolute_url(), "/post/first-post/")

    # Users Models

    def test_profile(self):
        self.assertEqual(str(self.profile1), "test_superuser Profile")
        width, height = 400, 400
        img = Image.new(mode="RGB", size=(width, height))
        img.save(
            "/Users/johnsolly/Documents/code/blogthedata/django_project/media/default.png")
        self.profile1.save()
        with Image.open(self.profile1.image.path) as img:
            self.assertEqual(img.height, 300)
            self.assertEqual(img.width, 300)


class TestForms(SetUp):
    def test_post_form_valid_data(self):
        form = PostForm(data={
            "title": "My Second Post",
            "slug": "second-post",
            "category": "productivity",
            "metadesc": "I can make you more productive!",
            "draft": False,
            # "metaimg" : ""
            # "metaimg"_mimetype : ""
            "snippet": "Do the things",
            "content": "Do the things. All the things",
            # date_posted : ""
            "author": self.user1
            # "likes"
            # "views"

        })

        self.assertTrue(form.is_valid())

    def test_post_form_no_data(self):
        post_form = PostForm(data={})
        self.assertFalse(post_form.is_valid())
        self.assertEqual(len(post_form.errors), 2)

    def test_comment_form_valid_data(self):
        form = CommentForm(data={"content": "Hello World!"})
        self.assertTrue(form.is_valid())

    # How to test when you can comment nothing??
    def test_comment_form_no_data_still_valid(self):
        form = CommentForm(data={})
        self.assertTrue(form.is_valid())

    # Users Forms
    def test_user_register_form_valid_data(self):
        user_form = UserRegisterForm(data={"username": "test",
                                           "email": "example@test.com",
                                           "password1": "Coff33cak3s!",
                                           "password2": "Coff33cak3s!",
                                           "secret_password": "African Swallows",
                                           "captcha_0": "dummy-value",
                                           "captcha_1": "PASSED"})
        self.assertTrue(user_form.is_valid())

    def test_user_update_form_valid_data(self):
        form = UserUpdateForm(data={"email": "example@test.com",
                                    "username": "test"})

        self.assertTrue(form.is_valid())

    # Might want to add image validation
    def test_profile_update_form_valid_data(self):
        form = ProfileUpdateForm(data={"image": "image1"})
        self.assertTrue(form.is_valid())


class TestMisc(SetUp):
    def test_user_exists(self):
        self.assertTrue(User.objects.filter(
            username="test_superuser").exists())

    def test_login(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')


if __name__ == "__main__":
    unittest.main()
