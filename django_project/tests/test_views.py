from .base import SetUp, message_in_response, create_several_posts
from django.urls import reverse
from blog.models import Post
from siteanalytics.models import Visitor
from blog.forms import PostForm
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


class TestViews(SetUp):
    """
    At a minimum, views should
    1 - Check template used
    2 - Verify any objects are the right ones and querysets contain the right items
    3 - Any forms are of the right class
    4 - Test relevant template logic
    """

    def test_home_view(self):  # TODO add check for draft post
        # Anonymous user
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/home.html")
        self.assertIsInstance(response.context["posts"][0], Post)
        # self.assertIsInstance(response.context["form"])

        # Access using super_user (should get posts in draft mode)
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.get(reverse("home"))

    def test_user_post_list_view(self):
        user_posts_url = reverse("user-posts", args=[self.super_user.username])
        response = self.client.get(user_posts_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/user_posts.html")

    def test_post_detail_view_anonymous_regular_post(self):
        post1_detail_url = reverse("post-detail", args=[self.post1.slug])
        response = self.client.get(post1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_detail.html")

    def test_post_detail_view_anonymous_draft_post(self):
        draft_post_detail_url = reverse("post-detail", args=[self.draft_post.slug])
        response = self.client.get(draft_post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/404_page.html")

    def test_post_detail_view_staff_sees_draft_post(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        draft_post_detail_url = reverse("post-detail", args=[self.draft_post.slug])
        response = self.client.get(draft_post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_detail.html")

    def test_create_post_view_GET(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.get(reverse("post-create"))
        self.assertTemplateUsed(response, "blog/post/add_post.html")
        self.assertIsInstance(response.context["form"], PostForm)

    def test_create_post_view_POST(self):
        data = {
            "title": "Test Post Create View",
            "slug": "test-post-create-view",
            "category": self.category1.id,
            "metadesc": "I can make you more productive!",
            "draft": False,
            # "metaimg" : ""
            "snippet": "Do the things",
            "content": "Do the things. All the things",
            # date_posted : ""
            "author": self.super_user,
            "metaimg_alt_txt": "Meta Image Alt-Text",
            # "likes"
            # "views"
        }

        # Admin can create posts
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )

        response = self.client.post(reverse("post-create"), data=data)
        self.assertRedirects(
            response,
            expected_url=reverse("post-detail", args=["test-post-create-view"]),
        )
        self.assertEqual(Post.objects.last().title, "Test Post Create View")

    # def test_create_post_view_anonymous_blocked(self):
    # Viewer cannot create posts (This throws an uncaught permissions error when tests are run in terminal)
    # self.client.login(username=self.basic_user.username,
    #                   password=self.basic_user_password)
    # data['author'] = self.basic_user
    # data['slug'] = "i-shouldnt-exist"
    # response = self.client.post(
    #     reverse("post-create"), data=data)
    # self.assertEqual(response.status_code, 403)

    def test_update_post_view_GET(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.get(reverse("post-update", args=[self.post1.slug]))
        self.assertTemplateUsed(response, "blog/post/edit_post.html")
        self.assertIsInstance(response.context["form"], PostForm)

    def test_update_post_view_POST(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        post1_detail_url = reverse("post-detail", args=[self.post1.slug])
        post1_update_url = reverse("post-update", args=[self.post1.slug])
        data = {
            "title": "My Updated First Post",
            "slug": "first-post",
            "category": self.category1.id,
            "metadesc": "Curious about your health? Look no further!",
            "draft": False,
            # "metaimg" : ""
            "snippet": "Long ago, the four nations lived together in harmony.",
            "content": "Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            "metaimg_alt_txt": "Meta Image Alt-Text Update",
            # date_posted : ""
            "author": self.super_user
            # "likes"
            # "views"
        }

        response = self.client.post(post1_update_url, data=data)
        self.assertRedirects(response, expected_url=post1_detail_url)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "My Updated First Post")

    def test_post_delete_view(self):
        post1_delete_url = reverse("post-delete", args=[self.post1.slug])
        self.assertTrue(Post.objects.filter(id=self.post1.id).exists())
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )

        response = self.client.get(post1_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_confirm_delete.html")
        response = self.client.post(post1_delete_url, follow=True)
        self.assertRedirects(response, expected_url=reverse("home"))
        self.assertFalse(Post.objects.filter(id=self.post1.id).exists())

    def test_post_delete_view_different_user(self):
        post1_delete_url = reverse("post-delete", args=[self.post1.slug])
        self.assertTrue(Post.objects.filter(id=self.post1.id).exists())
        self.client.login(
            username=self.basic_user.username, password=self.general_password
        )

        response = self.client.get(post1_delete_url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(id=self.post1.id).exists())

    def test_category_view_anonymous(self):
        # anonymous user
        category_url = reverse("blog-category", args=[self.category1.name])
        response = self.client.get(category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/categories.html")
        self.assertEqual(response.context["category"], self.category1)
        self.assertIsInstance(response.context["posts"][0], Post)
        self.assertEqual(response.context["posts"].count(), 1)

    def test_category_view_staff(self):
        category_url = reverse("blog-category", args=[self.category1.name])
        # Admin can see posts in a category even if they are drafts
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.get(category_url)
        self.assertEqual(response.context["posts"].count(), 2)

    def test_category_view_paginated(self):
        category_url = reverse("blog-category", args=[self.category1.name])
        # Paginated list appears when there are many posts
        create_several_posts(self.category1, self.super_user, 20)
        response = self.client.get(category_url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(response.context["posts"].count(), 5)  # 5 per page

    def test_category_view_paginated_second_page(self):
        category_url = reverse("blog-category", args=[self.category1.name])
        create_several_posts(self.category1, self.super_user, 20)
        # Paginated list works when user has moved forward at least one page
        response = self.client.get(category_url, {"page": 2})
        self.assertTrue(response.context["page_obj"].has_previous())

    def test_category_view_portfolio(self):
        portfolio_url = reverse("blog-category", args=["portfolio"])
        response = self.client.get(portfolio_url)
        self.assertEqual(response.status_code, 200)

    def test_search_view_blank(self):
        # Empty page if user didn't search for anything and manually typed in the search url (get)
        response = self.client.get(reverse("blog-search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/search_posts.html")

    def test_search_view_anonymous(self):
        # If anonymous, should be able to find a post.
        data = {"searched": "Post"}
        response = self.client.post(reverse("blog-search"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["posts"][0], self.post1)

    def test_search_view_staff(self):
        data = {"searched": "Post"}
        # If authenticated, can see drafts
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.post(reverse("blog-search"), data=data)
        anon_post_count = Post.objects.active().count()
        self.assertGreater(response.context["posts"].count(), anon_post_count)

    def test_register_view_happy_path(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertIsInstance(response.context["form"], UserRegisterForm)

        data = {
            "username": "test2",
            "email": "example2@test.com",
            "first_name": "Tester2",
            "last_name": "Smith",
            "password1": "Coff33cak3s!",
            "password2": "Coff33cak3s!",
            "secret_password": "African Swallows",
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
        }

        response = self.client.post(reverse("register"), data=data, follow=True)
        self.assertRedirects(response, expected_url=reverse("login"))
        self.assertTemplateUsed(response, "users/login.html")

    def test_register_view_wrong_secret_pass(self):
        data = {
            "username": "test2",
            "email": "example2@test.com",
            "first_name": "Tester2",
            "last_name": "Smith",
            "password1": "Coff33cak3s!",
            "password2": "Coff33cak3s!",
            "secret_password": "African Swallows",
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
        }

        data["secret_password"] = "Wrong Password"
        data["username"] = "test3"

        response = self.client.post(reverse("register"), data=data, follow=True)

        self.assertTrue(
            message_in_response(
                response, "Hmm, I don't think that is the right password"
            )
        )

    def test_profile_view(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertIsInstance(response.context["p_form"], ProfileUpdateForm)
        self.assertIsInstance(response.context["u_form"], UserUpdateForm)

    def test_profile_view_edit(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.post(
            reverse("profile"),
            data={"email": "test@modified.com", "username": "modified"},
        )
        self.assertTrue(message_in_response(response, "Your account has been updated"))
        self.super_user.refresh_from_db()
        self.assertEqual(self.super_user.email, "test@modified.com")
        self.assertEqual(self.super_user.username, "modified")

    def test_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_logout_view(self):
        self.client.login(
            username=self.super_user.username, password=self.general_password
        )
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/logout.html")

    def test_password_rest_view(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_reset.html")

    def test_password_reset_done_view(self):
        response = self.client.get(reverse("password_reset_done"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_reset_done.html")

    # def test_password_reset_confirm_view(self):
    #     # TODO

    def test_password_reset_complete(self):
        response = self.client.get(reverse("password_reset_complete"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_reset_complete.html")

    def test_sitemap_view(self):
        response = self.client.get(reverse("django.contrib.sitemaps.views.sitemap"))
        self.assertEqual(response.status_code, 200)

    def test_robots_view(self):
        response = self.client.get(reverse("robots_rule_list"))
        self.assertEqual(response.status_code, 200)
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-agent: *")

    def test_works_cited_view(self):
        response = self.client.get(reverse("works-cited"))
        self.assertEqual(response.status_code, 200)

    def test_privacy_view(self):
        response = self.client.get(reverse("privacy"))
        self.assertEqual(response.status_code, 200)

    def test_security_txt_view(self):
        response = self.client.get(reverse("security-txt"))
        self.assertEqual(response.status_code, 200)

    def test_security_pgp_key_view(self):
        response = self.client.get(reverse("security-pgp-key-txt"))
        self.assertEqual(response.status_code, 200)

    def test_leaflet_map_view(self):
        response = self.client.get(reverse("leaflet-map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "siteanalytics/leaflet_map.html")
        self.assertIsInstance(response.context["visitors"][0], Visitor)

    def test_openlayers_map_view(self):
        response = self.client.get(reverse("openlayers-map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "siteanalytics/openlayers_map.html")

    def test_maplibre_map_view(self):
        response = self.client.get(reverse("maplibre-map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "siteanalytics/maplibre_map.html")

    def test_mapbox_map_view(self):
        response = self.client.get(reverse("mapbox-map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "siteanalytics/mapbox_map.html")

    # def test_handler_404(self):
    #     response = self.client.get("doesnotexist")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "blog/404_page.html")
