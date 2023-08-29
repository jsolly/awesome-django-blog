# Python Standard Library Imports
from unittest.mock import patch

# Third-Party Imports
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

# Local Imports
from .base import SetUp
from blog.models import Post, Category, Comment
from blog.views import AllPostsView, HomeView, CategoryView
from blog.forms import PostForm, CommentForm
from users.forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from .utils import (
    create_several_posts,
    create_user,
    create_post,
    create_comment,
    message_in_response,
)


class TestViews(SetUp):
    def setUp(self):
        self.comment_only_user = create_user()  # Not a superuser
        self.super_user = create_user(super_user=True)

    @patch("blog.views.DatabaseStatus")
    def test_status_view(self, mock_db_status):
        mock_db_status.return_value.get_status.return_value = (10, 2, 500)
        response = self.client.get(reverse("status"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/status_page.html")

    def test_all_posts_view_shows_correct_posts(self):
        create_post(title="My First Post", slug="my-first-post")
        response = self.client.get("/all-posts/")
        self.assertEqual(len(response.context["posts"]), 1)
        self.assertContains(response, "My First Post")

    def test_all_posts_view_shows_pagination(self):
        post_count = AllPostsView.paginate_by + 1
        create_several_posts(number_of_posts=post_count)
        response = self.client.get("/all-posts/")
        self.assertContains(response, "Next")
        self.assertContains(response, "Last")

    def test_pagination_is_enabled_all_posts(self):
        post_count = AllPostsView.paginate_by + 1
        create_several_posts(number_of_posts=post_count)
        response = self.client.get(reverse("all-posts"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["posts"]), AllPostsView.paginate_by)

        response = self.client.get("/all-posts/?page=2")
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["page_obj"].object_list), 1)  # Last post

    def test_all_posts_view(self):
        create_post()
        response = self.client.get(reverse("all-posts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/all_posts.html")
        self.assertIsInstance(response.context["posts"][0], Post)

    def test_home_view_anonymous_user(self):  # TODO add check for draft post
        create_post()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/home.html")
        self.assertIsInstance(response.context["posts"][0], Post)

    def test_home_view_super_user(self):
        # Access using super_user (should get posts in draft mode)
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_view_htmx_request(self):
        headers = {"HTTP_HX-Request": "true", "HTTP_HX-Trigger": "TEST"}
        response = self.client.get(reverse("home"), **headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/parts/posts.html")

    def test_home_view_paginated(self):
        post_count = HomeView.paginate_by + 1
        create_several_posts(number_of_posts=post_count)
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context["posts"]), HomeView.paginate_by)
        self.assertEqual(response.context["page_obj"].has_next(), True)

    def test_post_detail_view_anonymous(self):
        test_post = create_post()
        test_post_detail_url = reverse("post-detail", args=[test_post.slug])
        response = self.client.get(test_post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_detail.html")

    def test_post_detail_view_anonymous_draft_post(self):
        draft_post = create_post(draft=True)
        draft_post_detail_url = reverse("post-detail", args=[draft_post.slug])
        response = self.client.get(draft_post_detail_url)
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_super_user_sees_draft_post(self):
        draft_post = create_post(draft=True)
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )
        draft_post_detail_url = reverse("post-detail", args=[draft_post.slug])
        response = self.client.get(draft_post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/post_detail.html")

    def test_post_create_view_has_correct_context_template_and_form(self):
        self.client.login(
            username=self.super_user.username, password=self.test_password
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
            "category": self.test_category.id,
            "metadesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "draft": False,
            "metaimg": SimpleUploadedFile(
                name="lorem_image.jpg",
                content=open("app/media/jsolly.webp", "rb").read(),
                content_type="image/webp",
            ),
            "snippet": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "author": self.super_user.id,
            "metaimg_alt_txt": "Lorem ipsum",
        }

        # Admin can create posts
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )

        response = self.client.post(reverse("post-create"), data=data)
        self.assertRedirects(
            response,
            expected_url=reverse("post-detail", args=[data["slug"]]),
        )
        self.assertEqual(Post.objects.last().title, data["title"])
        self.assertEqual(Post.objects.last().slug, data["slug"])
        self.assertEqual(Post.objects.last().category, self.test_category)
        self.assertEqual(Post.objects.last().metadesc, data["metadesc"])
        self.assertEqual(Post.objects.last().draft, data["draft"])
        self.assertEqual(Post.objects.last().snippet, data["snippet"])
        self.assertEqual(Post.objects.last().content, data["content"])
        self.assertEqual(Post.objects.last().author, self.super_user)
        self.assertEqual(Post.objects.last().metaimg_alt_txt, data["metaimg_alt_txt"])

    def test_create_post_view_comment_only_user_blocked(self):
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        data = {
            "title": "Lorem Ipsum Post",
            "slug": "lorem-ipsum-post",
            "category": self.test_category.id,
            "metadesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "draft": False,
            "author": self.comment_only_user.id,
        }
        response = self.client.post(reverse("post-create"), data=data)
        self.assertEqual(response.status_code, 403)

    def test_update_post_view_has_correct_context_template_and_form(self):
        test_post = create_post(author=self.super_user)
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )
        post1_update_url = reverse("post-update", args=[test_post.slug])
        response = self.client.get(post1_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/edit_post.html")
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(response.context["title"], f"Edit {test_post.title}")

    def test_update_post_view(self):
        test_post = create_post(author=self.comment_only_user)
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        post1_detail_url = reverse("post-detail", args=[test_post.slug])
        post1_update_url = reverse("post-update", args=[test_post.slug])
        new_category = Category.objects.create(name="New Category")
        data = {
            "title": "Updated First Post",
            "slug": test_post.slug,
            "category": new_category.id,
            "metadesc": "Updated Meta Description",
            "draft": False,
            "metaimg": SimpleUploadedFile(
                name="test_image.jpg",
                content=open("app/media/jsolly.webp", "rb").read(),
                content_type="image/webp",
            ),
            "snippet": "Long ago, the four nations lived together in harmony.",
            "content": "Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            "metaimg_alt_txt": "Meta Image Alt-Text Update",
            # date_posted : ""
            "author": self.comment_only_user
            # "likes"
            # "views"
        }

        response = self.client.post(post1_update_url, data=data)
        self.assertRedirects(response, expected_url=post1_detail_url)
        test_post.refresh_from_db()
        self.assertEqual(test_post.title, data["title"])
        self.assertEqual(test_post.category, new_category)
        self.assertEqual(test_post.metadesc, data["metadesc"])
        self.assertEqual(test_post.snippet, data["snippet"])
        self.assertEqual(test_post.content, data["content"])
        self.assertEqual(test_post.metaimg_alt_txt, data["metaimg_alt_txt"])

    def test_post_delete_view(self):
        test_post = create_post(author=self.super_user)
        post1_delete_url = reverse("post-delete", args=[test_post.slug])
        self.assertTrue(Post.objects.filter(id=test_post.id).exists())
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )

        response = self.client.get(post1_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_confirm_delete.html")
        response = self.client.post(post1_delete_url, follow=True)
        self.assertRedirects(response, expected_url=reverse("home"))
        self.assertFalse(Post.objects.filter(id=test_post.id).exists())

    def test_post_delete_view_different_user(self):
        test_post = create_post()
        post1_delete_url = reverse("post-delete", args=[test_post.slug])
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )

        response = self.client.get(post1_delete_url)  # Attempt to delete post
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        self.assertTrue(Post.objects.filter(id=test_post.id).exists())

    def test_create_comment_view(self):
        test_post = create_post()
        # Login to basic account to submit comment
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        test_post_detail_url = reverse("post-detail", args=[test_post.slug])
        test_post_comment_url = reverse("comment-create", args=[test_post.slug])

        response = self.client.post(
            test_post_comment_url,
            {
                "content": "Test comment",
                "post_slug": test_post.slug,
            },
        )
        # Redirect to post detail page after comment submission
        self.assertEqual(response.status_code, 302)
        # Ensure redirect to post after comment submission
        self.assertRedirects(response, test_post_detail_url)
        # Ensure a comment was added to the post
        self.assertEqual(test_post.comments.count(), 1)

    def test_create_comment_view_with_htmx(self):
        test_post = create_post()
        # Login to basic account to submit comment
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        test_post_comment_url = reverse("comment-create", args=[test_post.slug])
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(
            test_post_comment_url,
            {
                "content": "Test comment",
                "post_slug": test_post.slug,
            },
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_post.comments.count(), 1)

    def test_update_comment_view_has_correct_context_template_and_form(self):
        test_post = create_post(title="Edit This Post", slug="edit-this-post")
        test_comment = create_comment(post=test_post, author=self.comment_only_user)
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        response = self.client.get(reverse("comment-update", args=[test_comment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/comment/update_comment.html")
        self.assertIsInstance(response.context["form"], CommentForm)
        self.assertEqual(response.context["title"], f"Edit Comment #{test_comment.id}")
        self.assertEqual(
            response.context["description"], f"Edit Comment #{test_comment.id}"
        )
        self.assertEqual(response.context["comment"], test_comment)

    def test_update_comment_view(self):
        test_post = create_post(title="Edit This Post", slug="edit-this-post")
        test_comment = create_comment(post=test_post, author=self.comment_only_user)
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        updated_content = "Updated comment content"

        response = self.client.post(
            reverse("comment-update", args=[test_comment.id]),
            {"content": updated_content},
        )

        self.assertRedirects(
            response, reverse("post-detail", args=[test_post.slug]) + "#comments"
        )
        test_comment.refresh_from_db()
        self.assertEqual(test_comment.content, updated_content)

    def test_comment_delete_view_with_htmx(self):
        test_post = create_post(title="Delete This Post", slug="delete-this-post")
        test_comment = create_comment(post=test_post, author=self.comment_only_user)
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )

        headers = {"HTTP_HX-Request": "true"}
        response = self.client.delete(
            reverse("comment-delete", args=[test_comment.id]), **headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason_phrase, "Comment deleted successfully")
        self.assertFalse(Comment.objects.filter(id=test_comment.id).exists())

    def test_comment_delete_view_without_htmx(self):
        test_post = create_post(title="Delete This Post", slug="delete-this-post")
        test_comment = create_comment(post=test_post, author=self.comment_only_user)
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )

        response = self.client.delete(reverse("comment-delete", args=[test_comment.id]))
        self.assertRedirects(response, reverse("post-detail", args=[test_post.slug]))
        self.assertFalse(Comment.objects.filter(id=test_comment.id).exists())

    def test_category_view_anonymous(self):
        create_post()
        category_url = reverse("blog-category", args=[self.test_category.slug])
        response = self.client.get(category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/categories.html")
        self.assertEqual(response.context["category"], self.test_category)
        self.assertIsInstance(response.context["posts"][0], Post)
        self.assertEqual(response.context["posts"].count(), 1)

    def test_category_view_htmx_request(self):
        category_url = reverse("blog-category", args=[self.test_category.slug])
        headers = {"HTTP_HX-Request": "true", "HTTP_HX-Trigger": "test"}
        response = self.client.get(category_url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/parts/posts.html")

    def test_category_view_staff(self):
        create_post(draft=True)
        category_url = reverse("blog-category", args=[self.test_category.slug])
        # Admin can see posts in a category even if they are drafts
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )
        response = self.client.get(category_url)
        self.assertEqual(response.context["posts"].count(), 1)

    def test_category_view_paginated(self):
        post_count = CategoryView.paginate_by
        category_url = reverse("blog-category", args=[self.test_category.slug])
        # Paginated list appears when there are more than paginate_by posts
        create_several_posts(post_count + 1)
        response = self.client.get(category_url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(
            response.context["posts"].count(), CategoryView.paginate_by
        )  # 3 per page

    def test_category_view_paginated_second_page(self):
        post_count = CategoryView.paginate_by + 1
        category_url = reverse("blog-category", args=[self.test_category.slug])
        create_several_posts(post_count)
        # Paginated list works when user has moved forward at least one page
        response = self.client.get(category_url, {"page": 2})
        self.assertTrue(response.context["page_obj"].has_previous())

    def test_portfolio_view(self):
        portfolio_url = reverse("portfolio")
        response = self.client.get(portfolio_url)
        self.assertEqual(response.status_code, 200)

    def test_search_view_blank(self):
        # Empty page if user didn't search for anything and manually typed in the search url (get)
        response = self.client.get(reverse("blog-search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/search_posts.html")

    def test_search_view_anonymous(self):
        test_post = create_post()
        # If anonymous, should be able to find a post.
        data = {"searched": test_post.title}
        response = self.client.get(reverse("blog-search"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["posts"][0], test_post)

    def test_search_view_staff(self):
        create_post()
        create_post(draft=True)
        data = {"searched": "Default Title"}
        # If authenticated, can see drafts
        self.client.login(
            username=self.super_user.username, password=self.test_password
        )
        response = self.client.get(reverse("blog-search"), data=data)
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
            username=self.comment_only_user.username, password=self.test_password
        )
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertIsInstance(response.context["p_form"], ProfileUpdateForm)
        self.assertIsInstance(response.context["u_form"], UserUpdateForm)

    def test_profile_view_edit(self):
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
        )
        response = self.client.post(
            reverse("profile"),
            data={"email": "test@modified.com", "username": "modified"},
        )
        self.assertTrue(
            message_in_response(response, "Your account has been updated. Thanks!")
        )
        self.comment_only_user.refresh_from_db()
        self.assertEqual(self.comment_only_user.email, "test@modified.com")
        self.assertEqual(self.comment_only_user.username, "modified")

    def test_profile_view_edit_invalid(self):
        self.client.login(
            username=self.comment_only_user.username, password=self.test_password
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
            username=self.comment_only_user.username, password=self.test_password
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
