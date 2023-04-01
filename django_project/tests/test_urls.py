from .base import SetUp
from django.urls import resolve, reverse
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from robots.views import RuleList
from blog.views import (
    HomeView,
    AllPostsView,
    CreatePostView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CategoryView,
    SearchView,
    PortfolioView,
    StatusView,
)
from django_project.views import (
    works_cited_view,
    security_txt_view,
    security_pgp_key_view,
)
from users.views import (
    register_view,
    profile_view,
    MyLoginView,
    MyLogoutView,
    MyPasswordResetView,
    MyPasswordResetDoneView,
    MyPasswordResetCompleteView,
)


def get_url(url_name):
    return resolve(reverse(url_name))


class TestUrls(SetUp):
    def test_status_page_url_is_resolved(self):
        self.assertEqual(resolve(reverse("status")).func.view_class, StatusView)

    def test_all_posts_url_is_resolved(self):
        self.assertEqual(resolve(reverse("all-posts")).func.view_class, AllPostsView)

    def test_home_url_is_resolved(self):
        self.assertEqual(resolve(reverse("home")).func.view_class, HomeView)

    def test_create_post_url_is_resolved(self):
        self.assertEqual(
            resolve(reverse("post-create")).func.view_class, CreatePostView
        )

    def test_post_detail_url_is_resolved(self):
        post1_detail_url = reverse("post-detail", args=[self.post1.slug])
        self.assertEqual(resolve(post1_detail_url).func.view_class, PostDetailView)

    def test_post_update_url_is_resolved(self):
        post1_update_url = reverse("post-update", args=[self.post1.slug])
        self.assertEqual(resolve(post1_update_url).func.view_class, PostUpdateView)

    def test_post_delete_url_is_resolved(self):
        post1_delete_url = reverse("post-delete", args=[self.post1.slug])
        self.assertEqual(resolve(post1_delete_url).func.view_class, PostDeleteView)

    def test_category_url_is_resolved(self):
        category_url = reverse("blog-category", args=[self.category1.name])
        self.assertEqual(resolve(category_url).func.view_class, CategoryView)

    def test_portfolio_url_is_resolved(self):
        self.assertEqual(resolve(reverse("portfolio")).func.view_class, PortfolioView)

    def test_search_url_is_resolved(self):
        self.assertEqual(resolve(reverse("blog-search")).func.view_class, SearchView)

    def test_register_url_is_resolved(self):
        self.assertEqual(resolve(reverse("register")).func, register_view)

    def test_profile_url_is_resolved(self):
        self.assertEqual(resolve(reverse("profile")).func, profile_view)

    def test_login_url_is_resolved(self):
        self.assertEqual(resolve(reverse("login")).func.view_class, MyLoginView)
        self.assertEqual(f"/{settings.LOGIN_URL}/", reverse("login"))

    def test_logout_url_is_resolved(self):
        self.assertEqual(resolve(reverse("logout")).func.view_class, MyLogoutView)

    def test_sitemap_url_is_resolved(self):
        self.assertEqual(
            resolve(reverse("django.contrib.sitemaps.views.sitemap")).func, sitemap
        )

    def test_robots_url_is_resolved(self):
        self.assertEqual(resolve(reverse("robots_rule_list")).func.view_class, RuleList)

    def test_works_cited_url_is_resolved(self):
        self.assertEqual(resolve(reverse("works-cited")).func, works_cited_view)

    def test_security_txt_url_is_resolved(self):
        self.assertEqual(get_url("security-txt").func, security_txt_view)

    def test_security_pgp_key_url_is_resolved(self):
        self.assertEqual(get_url("security-pgp-key-txt").func, security_pgp_key_view)

    # def test_admin_url_is_resolved(self): # wasn't able to figure this one out
    #             self.assertIsInstance(
    #         resolve(reverse("admin:index")).func, AdminSite.index)

    def test_password_reset_url_is_resolved(self):
        self.assertEqual(get_url("password_reset").func.view_class, MyPasswordResetView)

    def test_password_resset_done_url_is_resolved(self):
        self.assertEqual(
            get_url("password_reset_done").func.view_class, MyPasswordResetDoneView
        )

    # def test_password_reset_confirm_url_is_resolved(self): #TODO
    #     self.assertEqual(get_url("password_reset_confirm").func.view_class, MyPasswordResetConfirmView)

    def test_password_reset_complete_url_is_resolved(self):
        self.assertEqual(
            get_url("password_reset_complete").func.view_class,
            MyPasswordResetCompleteView,
        )

    # def test_captcha_url_is_resolved(self):
    #     self.assertEqual(resolve(reverse("logout")).func.view_class, MyLogoutView)
