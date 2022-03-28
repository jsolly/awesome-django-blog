from distutils.errors import LinkError
import os
from django.test import TestCase
from django import setup
from django.urls import resolve, reverse
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()

from .models import Post
from .views import (
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
    SearchView
)

class TestUrls(TestCase):
    def test_home_url_is_resolved(self):
        url = reverse("blog-home")
        self.assertEqual(resolve(url).func.view_class, HomeView)

    def test_user_posts_url_is_resolved(self):
        url = reverse("user-posts", args=['John_Solly'])
        self.assertEqual(resolve(url).func.view_class, UserPostListView)


    def test_create_post_url_is_resolved(self):
        url = reverse("post-create")
        self.assertEqual(resolve(url).func.view_class, CreatePostView)

    def test_post_detail_url_is_resolved(self):
        url = reverse("post-detail", args=['some-slug'])
        self.assertEqual(resolve(url).func.view_class, PostDetailView)

    def test_post_update_url_is_resolved(self):
        url = reverse("post-update", args=['some-slug'])
        self.assertEqual(resolve(url).func.view_class, PostUpdateView)

    def test_post_delete_url_is_resolved(self):
        url = reverse("post-delete", args=['some-slug'])
        self.assertEqual(resolve(url).func.view_class, PostDeleteView)

    def create_comment_url_is_resolved(self):
        url = reverse("create-comment")
        self.assertEqual(resolve(url).func.view_class, CreateCommentView)

    def category_url_is_resolved(self):
        url = reverse("category-url")
        self.assertEqual(resolve(url).func.view_class, CategoryView)

    def about_url_is_resolved(self):
        url = reverse("blog-about")
        self.assertEqual(resolve(url).func.view_class, AboutView)

    def post_like_url_is_resolved(self):
        url = reverse("blog-about")
        self.assertEqual(resolve(url).func.view_class, PostLikeView)

    def roadmap_url_is_resolved(self):
        url = reverse("blog-roadmap")
        self.assertEqual(resolve(url).func.view_class, RoadMapView)
    
    def test_search_url_is_resolved(self):
        url = reverse("blog-search")
        self.assertEqual(resolve(url).func, SearchView)
class PostTestCase(TestCase):
    def test_queryset_exists(self):
        qs = Post.objects.all()
        self.assertTrue(qs.exists)