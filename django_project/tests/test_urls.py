from .base import SetUp
from django.urls import resolve, reverse
from django.conf import settings
from django.contrib.auth import views as auth_views
from admin_honeypot.views import AdminHoneypot
from robots.views import RuleList
from django.contrib.sitemaps.views import sitemap
from blog.views import (
    HomeView,
    UserPostListView,
    CreatePostView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CreateCommentView,
    CategoryView,
    about_view,
    post_like_view,
    road_map_view,
    search_view,
    unit_test_view,
    works_cited_view,
    security_txt_view,
    security_pgp_key_view
)
from users.views import register_view, profile_view

def get_url(url_name):
    return resolve(reverse(url_name))

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
            resolve(self.post1_update_url).func.view_class, PostUpdateView)

    def test_post_delete_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post1_delete_url).func.view_class, PostDeleteView)

    def test_create_comment_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post1_create_comment_url).func.view_class, CreateCommentView)

    def test_category_url_is_resolved(self):
        self.assertEqual(
            resolve(self.category_url).func.view_class, CategoryView)

    def test_about_url_is_resolved(self):
        self.assertEqual(resolve(self.about_url).func, about_view)

    def test_post_like_url_is_resolved(self):
        self.assertEqual(
            resolve(self.post1_like_url).func, post_like_view)

    def test_roadmap_url_is_resolved(self):
        self.assertEqual(
            resolve(self.roadmap_url).func, road_map_view)

    def test_search_url_is_resolved(self):
        self.assertEqual(resolve(self.search_url).func, search_view)

    def test_unittest_url_is_resolved(self):
        self.assertEqual(
            resolve(self.unittest_url).func, unit_test_view)

    def test_register_url_is_resolved(self):
        self.assertEqual(resolve(self.register_url).func, register_view)

    def test_profile_url_is_resolved(self):
        self.assertEqual(resolve(self.profile_url).func, profile_view)

    def test_login_url_is_resolved(self):
        self.assertEqual(
            resolve(self.login_url).func.view_class, auth_views.LoginView)
        self.assertEqual(f"/{settings.LOGIN_URL}/", self.login_url)

    def test_logout_url_is_resolved(self):
        self.assertEqual(
            resolve(self.logout_url).func.view_class, auth_views.LogoutView)

    def test_admin_honey_pot_url_is_resolved(self):
        self.assertEqual(resolve(self.honey_pot_url).func.view_class, AdminHoneypot)
    
    def test_sitemap_url_is_resolved(self):
        self.assertEqual(resolve(self.sitemap_url).func, sitemap)

    def test_robots_url_is_resolved(self):
        self.assertEqual(resolve(self.robots_url).func.view_class, RuleList)
    
    def test_works_cited_url_is_resolved(self):
        self.assertEqual(resolve(self.works_cited_url).func, works_cited_view)

    def test_security_txt_url_is_resolved(self):
        self.assertEqual(get_url("security-txt").func, security_txt_view)


    def test_security_pgp_key_url_is_resolved(self):
        self.assertEqual(get_url("security-pgp-key-txt").func, security_pgp_key_view)


        
    # def test_admin_url_is_resolved(self): # wasn't able to figure this one out
    #             self.assertIsInstance(
    #         resolve(self.admin_url).func, AdminSite.index)

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
