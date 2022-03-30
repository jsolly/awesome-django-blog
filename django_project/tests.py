import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
setup()
from django.test import TestCase, Client
from django.urls import resolve, reverse
from blog.views import (
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
from blog.models import Post
from users.models import User


class SetUp(TestCase):
    """Create User and Post object to be shared by tests. Also create urls using reverse()"""

    def setUp(self):

        # User Object
        self.user1 = User.objects.create_superuser(username="test_superuser")

        # Post Object
        self.post1 = Post.objects.create(
            title="My first Post",
            slug="first-post",
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
        self.client = Client()
        self.home_url = reverse('blog-home')
        self.post_detail_url = reverse("post-detail", args=[self.post1.slug])
        self.post_create_url = reverse("post-create")
        self.user_posts_url = reverse("user-posts", args=[self.user1.username])
        self.post_update_url = reverse("post-update", args=['some-slug'])
        self.post_delete_url = reverse("post-delete", args=['some-slug'])
        self.create_comment_url = reverse("comment-create", args=['some-slug'])
        self.category_url = reverse("blog-category", args=['health'])
        self.about_url = reverse("blog-about")
        self.post_like_url = reverse("post-like", args=['some-slug'])
        self.blog_roadmap_url = reverse("blog-roadmap")
        self.search_url = reverse("blog-search")
        self.unittest_url = reverse("blog-unittest")


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
            resolve(self.post_detail_url).func.view_class, PostDetailView)

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
            resolve(self.post_like_url).func, PostLikeView)

    def test_roadmap_url_is_resolved(self):
        self.assertEqual(
            resolve(self.blog_roadmap_url).func, RoadMapView)

    def test_search_url_is_resolved(self):
        self.assertEqual(resolve(self.search_url).func, SearchView)

    def test_unittest_url_is_resolved(self):
        self.assertEqual(resolve(self.unittest_url).func, UnitTestView)


class TestViews(SetUp):

    def test_home_view(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('blog/home.html' in response.template_name)

    def test_user_post_list_view(self):
        response = self.client.get(self.user_posts_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('blog/user_posts.html' in response.template_name)

    def test_post_detail_view(self):
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('blog/post_detail.html' in response.template_name)

    # def test_create_post_view(self):  # TODO: Need to figure out how to create a session
    #     response = self.client.get(self.post_create_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue('blog/add_post.html' in response.template_name)

    def test_about_view(self): # TODO: Not sure how to check templates in function based view
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)
    
    def test_unittest_view(self): # TODO: Not sure how to check templates in function based view
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)


# class PostTestCase(TestCase):
#     def test_queryset_exists(self):
#         query_set = Post.objects.all()
#         self.assertTrue(query_set.exists)

if __name__ == "__main__":
    print("Hello world!")