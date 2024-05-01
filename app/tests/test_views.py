# Local Imports
from .base import SetUp

from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from users.forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from .utils import (
    create_unique_post,
    create_comment,
    message_in_response,
)

# Python Standard Library Imports
from unittest.mock import patch

# Third-Party Imports
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User


class TestViews(SetUp):
    @patch("blog.views.DatabaseStatus")
    def test_status_view(self, mock_db_status):
        mock_db_status.return_value.get_status.return_value = (10, 2, 500)
        response = self.client.get(reverse("status"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/status_page.html")

    # def test_all_posts_view_shows_pagination(self):
    #     response = self.client.get("/all-posts/")
    #     self.assertContains(response, "Next")
    #     self.assertContains(response, "Last")

    # def test_pagination_is_enabled_all_posts(self):
    #     response = self.client.get(reverse("all-posts"))
    #     self.assertTrue(response.context["is_paginated"])
    #     self.assertEqual(len(response.context["posts"]), AllPostsView.paginate_by)

    #     response = self.client.get("/all-posts/?page=2")
    #     self.assertEqual(response.context["page_obj"].number, 2)
    #     self.assertEqual(len(response.context["page_obj"].object_list), 1)  # Last post

    def test_all_posts_view(self):
        response = self.client.get(reverse("all-posts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/all_posts.html")
        self.assertIsInstance(response.context["posts"][0], Post)

    def test_home_view_anonymous_user(self):  # TODO add check for draft post
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/home.html")
        self.assertIsInstance(response.context["posts"][0], Post)

    def test_home_view_admin_user(self):
        # Access using admin_user (should get posts in draft mode)
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_view_htmx_request(self):
        headers = {"HTTP_HX-Request": "true", "HTTP_HX-Trigger": "TEST"}
        response = self.client.get(reverse("home"), **headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/parts/posts.html")

    # def test_home_view_paginated(self):
    #     response = self.client.get(reverse("home"))
    #     self.assertEqual(len(response.context["posts"]), HomeView.paginate_by)
    #     self.assertEqual(response.context["page_obj"].has_next(), True)

    def test_post_detail_view_anonymous(self):
        test_post_detail_url = reverse("post-detail", args=[self.first_post.slug])
        response = self.client.get(test_post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_detail.html")

    def test_post_detail_view_anonymous_draft_post(self):
        draft_post_detail_url = reverse("post-detail", args=[self.draft_post.slug])
        response = self.client.get(draft_post_detail_url)
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_admin_user_sees_draft_post(self):
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        draft_post_detail_url = reverse("post-detail", args=[self.draft_post.slug])
        response = self.client.get(draft_post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_detail.html")

    def test_post_create_view_has_correct_context_template_and_form(self):
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        response = self.client.get(reverse("post-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/add_post.html")
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(response.context["title"], "Create a New Post")

    def test_create_post_view(self):
        data = {
            "title": "Lorem Ipsum Post",
            "slug": "lorem-ipsum-post",
            "category": self.default_category.id,
            "metadesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "draft": False,
            "metaimg": SimpleUploadedFile(
                name="lorem_image.jpg",
                content=open("app/media/default.webp", "rb").read(),
                content_type="image/webp",
            ),
            "snippet": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "author": self.admin_user.id,
            "metaimg_alt_txt": "Lorem ipsum",
        }

        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )

        response = self.client.post(reverse("post-create"), data=data)
        self.assertRedirects(
            response,
            expected_url=reverse("post-detail", args=[data["slug"]]),
        )
        self.assertEqual(Post.objects.last().title, data["title"])
        self.assertEqual(Post.objects.last().slug, data["slug"])
        self.assertEqual(Post.objects.last().category, self.default_category)
        self.assertEqual(Post.objects.last().metadesc, data["metadesc"])
        self.assertEqual(Post.objects.last().draft, data["draft"])
        self.assertEqual(Post.objects.last().snippet, data["snippet"])
        self.assertEqual(Post.objects.last().content, data["content"])
        self.assertEqual(Post.objects.last().author, self.admin_user)
        self.assertEqual(Post.objects.last().metaimg_alt_txt, data["metaimg_alt_txt"])

    def test_create_post_view_comment_only_user_blocked(self):
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )
        data = {
            "title": "Lorem Ipsum Post",
            "slug": "lorem-ipsum-post",
            "category": self.default_category.id,
            "metadesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "draft": False,
            "author": self.comment_only_user.id,
        }
        response = self.client.post(reverse("post-create"), data=data)
        self.assertEqual(response.status_code, 403)

    def test_update_post_view_has_correct_context_template_and_form(self):
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        post1_update_url = reverse("post-update", args=[self.first_post.slug])
        response = self.client.get(post1_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/edit_post.html")
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(response.context["title"], f"Edit {self.first_post.title}")

    def test_update_post_view(self):
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        post1_detail_url = reverse("post-detail", args=[self.first_post.slug])
        post1_update_url = reverse("post-update", args=[self.first_post.slug])
        data = {
            "title": "Updated First Post",
            "slug": self.first_post.slug,
            "category": self.first_post.category.id,
            "metadesc": "Updated Meta Description",
            "draft": False,
            "metaimg": SimpleUploadedFile(
                name="test_image.jpg",
                content=open("app/media/default.webp", "rb").read(),
                content_type="image/webp",
            ),
            "snippet": "Long ago, the four nations lived together in harmony.",
            "content": "Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            "metaimg_alt_txt": "Meta Image Alt-Text Update",
            # date_posted : ""
            "author": self.admin_user,
            # "likes"
            # "views"
        }

        response = self.client.post(post1_update_url, data=data)
        self.assertRedirects(response, expected_url=post1_detail_url)
        self.first_post.refresh_from_db()
        self.assertEqual(self.first_post.title, data["title"])
        self.assertEqual(self.first_post.metadesc, data["metadesc"])
        self.assertEqual(self.first_post.snippet, data["snippet"])
        self.assertEqual(self.first_post.content, data["content"])
        self.assertEqual(self.first_post.metaimg_alt_txt, data["metaimg_alt_txt"])

    def test_post_delete_view(self):
        delete_me_post = create_unique_post()
        post1_delete_url = reverse("post-delete", args=[delete_me_post.slug])
        self.assertTrue(Post.objects.filter(id=delete_me_post.id).exists())
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )

        response = self.client.get(post1_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_confirm_delete.html")
        response = self.client.post(post1_delete_url, follow=True)
        self.assertRedirects(response, expected_url=reverse("home"))
        self.assertFalse(Post.objects.filter(id=delete_me_post.id).exists())

    def test_create_comment_view(self):
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )
        test_post_detail_url = reverse("post-detail", args=[self.first_post.slug])
        test_post_comment_url = reverse("comment-create", args=[self.first_post.slug])

        first_post_comment_count = self.first_post.comments.count()

        response = self.client.post(
            test_post_comment_url,
            {
                "content": "Test comment",
                "post_slug": self.first_post.slug,
            },
        )
        # Redirect to post detail page after comment submission
        self.assertEqual(response.status_code, 302)
        # Ensure redirect to post after comment submission
        self.assertRedirects(response, test_post_detail_url + "#comments")
        # Ensure a comment was added to the post
        self.assertEqual(self.first_post.comments.count(), first_post_comment_count + 1)

    def test_create_comment_view_with_htmx(self):
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )
        first_post_comment_count = self.first_post.comments.count()
        test_post_comment_url = reverse("comment-create", args=[self.first_post.slug])
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(
            test_post_comment_url,
            {
                "content": "Test comment",
                "post_slug": self.first_post.slug,
            },
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.first_post.comments.count(), first_post_comment_count + 1)

    def test_update_comment_view_has_correct_context_template_and_form(self):
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )
        unqiue_comment = create_comment(post=self.first_post)
        response = self.client.get(reverse("comment-update", args=[unqiue_comment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/comment/update_comment.html")
        self.assertIsInstance(response.context["form"], CommentForm)
        self.assertEqual(
            response.context["title"], f"Edit Comment #{unqiue_comment.id}"
        )
        self.assertEqual(
            response.context["description"], f"Edit Comment #{unqiue_comment.id}"
        )
        self.assertEqual(response.context["comment"], unqiue_comment)

    def test_update_comment_view(self):
        update_me_comment = create_comment(
            post=self.first_post, author=self.comment_only_user
        )
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )
        updated_content = "Updated comment content"

        response = self.client.post(
            reverse("comment-update", args=[update_me_comment.id]),
            {"content": updated_content},
        )

        self.assertRedirects(
            response, reverse("post-detail", args=[self.first_post.slug]) + "#comments"
        )
        update_me_comment.refresh_from_db()
        self.assertEqual(update_me_comment.content, updated_content)

    def test_comment_delete_view_with_htmx(self):
        delete_me_comment = create_comment(
            post=self.first_post, author=self.comment_only_user.username
        )
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )

        headers = {"HTTP_HX-Request": "true"}
        response = self.client.delete(
            reverse("comment-delete", args=[delete_me_comment.id]), **headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason_phrase, "Comment deleted successfully")
        self.assertFalse(Comment.objects.filter(id=delete_me_comment.id).exists())

    def test_comment_delete_view_without_htmx(self):
        delete_me_comment = create_comment(
            post=self.first_post, author=self.comment_only_user
        )
        self.client.login(
            username=self.comment_only_user.username,
            password=self.comment_only_user_password,
        )

        response = self.client.delete(
            reverse("comment-delete", args=[delete_me_comment.id])
        )
        self.assertRedirects(
            response, reverse("post-detail", args=[self.first_post.slug])
        )
        self.assertFalse(Comment.objects.filter(id=delete_me_comment.id).exists())

    def test_comment_delete_different_user_blocked(self):
        first_comment = self.first_comment
        comment_only_user_2 = User.objects.create_user(
            username="comment_only_user_2",
            email="comment_only_user2@example.com",
            password="testpassword",
        )
        self.client.login(
            username=comment_only_user_2.username, password="testpassword"
        )
        response = self.client.delete(
            reverse("comment-delete", args=[first_comment.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(id=first_comment.id).exists())

    def test_category_view_anonymous(self):
        category_url = reverse("blog-category", args=[self.default_category.slug])
        response = self.client.get(category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/categories.html")
        self.assertEqual(response.context["category"], self.default_category)
        self.assertIsInstance(response.context["posts"][0], Post)

    def test_category_view_htmx_request(self):
        category_url = reverse("blog-category", args=[self.default_category.slug])
        headers = {"HTTP_HX-Request": "true", "HTTP_HX-Trigger": "test"}
        response = self.client.get(category_url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/parts/posts.html")

    # def test_category_view_paginated(self):
    #     category_url = reverse("blog-category", args=[self.default_category.slug])
    #     # Paginated list appears when there are more than paginate_by posts
    #     response = self.client.get(category_url)
    #     self.assertTrue(response.context["is_paginated"])
    #     self.assertEqual(
    #         response.context["posts"].count(), CategoryView.paginate_by
    #     )  # 3 per page

    # def test_category_view_paginated_second_page(self):
    #     category_url = reverse("blog-category", args=[self.default_category.slug])
    #     # Paginated list works when user has moved forward at least one page
    #     response = self.client.get(category_url, {"page": 2})
    #     self.assertTrue(response.context["page_obj"].has_previous())


    def test_search_view_blank(self):
        # Empty page if user didn't search for anything and manually typed in the search url (get)
        response = self.client.get(reverse("blog-search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/search_posts.html")

    def test_search_view_anonymous(self):
        # If anonymous, should be able to find a post
        data = {"searched": self.first_post.title}
        response = self.client.get(reverse("blog-search"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["posts"][0], self.first_post)

    def test_search_view_staff(self):
        data = {"searched": self.draft_post.title}
        # If authenticated, can see drafts
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        response = self.client.get(reverse("blog-search"), data=data)
        self.assertEqual(response.status_code, 200)

        posts_in_response = response.context["posts"]
        self.assertEqual(posts_in_response.count(), 1)

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
            username=self.admin_user.username, password=self.admin_user_password
        )
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertIsInstance(response.context["p_form"], ProfileUpdateForm)
        self.assertIsInstance(response.context["u_form"], UserUpdateForm)

    # def test_profile_view_edit(self):
    #     new_user = User.objects.get_or_create(
    #         username="test2",
    #         email="test2@example.com",
    #         password="testpassword",
    #     )[0]
    #     self.client.login(username=new_user.username, password="testpassword")
    #     response = self.client.post(
    #         reverse("profile"),
    #         data={"email": "test2@modified.com", "username": "modified"},
    #     )
    #     self.assertTrue(
    #         message_in_response(response, "Your account has been updated. Thanks!")
    #     )
    #     self.comment_only_user.refresh_from_db()
    #     self.assertEqual(new_user, "test@modified.com")
    #     self.assertEqual(new_user, "modified")

    def test_profile_view_edit_invalid(self):
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        response = self.client.post(
            reverse("profile"),
            data={"email": "invalid", "username": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertIsInstance(response.context["p_form"], ProfileUpdateForm)
        self.assertIsInstance(response.context["u_form"], UserUpdateForm)

    def test_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_logout_view(self):
        self.client.login(
            username=self.admin_user.username, password=self.admin_user_password
        )
        response = self.client.post(reverse("logout"))
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

    @patch("openai.Completion.create")
    def test_generate_gpt_input_title(self, mock_create):
        mock_create.return_value = {"choices": [{"text": "mocked response"}]}
        headers = {"HTTP_HX-Trigger": "generate-title"}
        response = self.client.post(
            "/generate-with-gpt/", data={"content": "my test blog content"}, **headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("mocked response", response.content.decode())

    def test_generate_gpt_input_title_empty(self):
        headers = {"HTTP_HX-Trigger": "generate-title"}
        response = self.client.post(
            "/generate-with-gpt/", data={"content": ""}, **headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No content found in the post content field", response.content.decode()
        )

    @patch("openai.Completion.create")
    def test_generate_gpt_input_slug(self, mock_create):
        mock_create.return_value = {"choices": [{"text": "mocked-response"}]}
        headers = {"HTTP_HX-Trigger": "generate-slug"}
        response = self.client.post(
            "/generate-with-gpt/",
            data={"title": "my test blog title"},
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("mocked-response", response.content.decode())

    def test_generate_gpt_input_slug_empty(self):
        headers = {"HTTP_HX-Trigger": "generate-slug"}
        response = self.client.post(
            "/generate-with-gpt/",
            data={"title": ""},
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No content found in the post title field", response.content.decode()
        )

    @patch("openai.Completion.create")
    def test_generate_gpt_input_metadesc(self, mock_create):
        mock_create.return_value = {"choices": [{"text": "mocked response"}]}
        headers = {"HTTP_HX-Trigger": "generate-metadesc"}
        response = self.client.post(
            "/generate-with-gpt/",
            data={"content": "my test blog content"},
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("mocked response", response.content.decode())

    def test_generate_gpt_input_metadesc_empty(self):
        headers = {"HTTP_HX-Trigger": "generate-metadesc"}
        response = self.client.post(
            "/generate-with-gpt/",
            data={"content": ""},
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No content found in the post content field", response.content.decode()
        )

    @patch("openai.Embedding.create")
    @patch("openai.Completion.create")
    def test_answer_question_with_gpt(
        self, mock_completion_create, mock_embedding_create
    ):
        mock_embedding_create.return_value = {"data": [{"embedding": [0.1] * 1536}]}
        mock_completion_create.return_value = {"choices": [{"text": "mocked response"}]}
        response = self.client.post(
            "/answer-with-gpt/", data={"question-text-area": "Test question?"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("mocked response", response.content.decode())
