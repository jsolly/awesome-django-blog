from .base import SetUp
from django.urls import reverse
from PIL import Image
from blog.models import Post, Comment, Category, slugify_instance
from users.models import Profile
from django.contrib.auth.models import User
from django.utils.text import slugify
from .base import SetUp


class TestModels(SetUp):
    def test_post_manager(self):
        active_posts = Post.objects.active()
        self.assertIsInstance(active_posts[0], Post)

    def test_category_absolute_url(self):
        test_category = Category.objects.get(name="Uncategorized")
        self.assertEqual(
            test_category.get_absolute_url(),
            "/category/uncategorized/",
        )

    # Users Models
    def test_profile(self):
        admin = User.objects.get(username="admin")
        profile1 = Profile.objects.get(user=admin)
        self.assertEqual(str(profile1), f"{admin.username} Profile")
        self.assertEqual(profile1.get_absolute_url(), reverse("profile"))
        width, height = 400, 400
        img = Image.new(mode="RGB", size=(width, height))
        img.save(profile1.image.path)
        profile1.save()
        with Image.open(profile1.image.path) as img:
            self.assertEqual(img.height, 300)
            self.assertEqual(img.width, 300)

    def test_create_comment(self):
        test_post = Post.objects.first()
        admin = User.objects.get(username="admin")
        comment = Comment.objects.create(
            post=test_post,
            author=admin,
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        )
        self.assertEqual(comment.post, test_post)
        self.assertEqual(comment.author, admin)
        self.assertEqual(
            comment.content, "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
        # Delete the comment
        comment.delete()

    def test_comment_print_and_absolute_url(self):
        test_comment = self.first_post.comments.first()
        self.assertEqual(
            str(test_comment), f"Comment '{test_comment.content}' by admin"
        )
        self.assertEqual(
            test_comment.get_absolute_url(), f"/post/{self.first_post.slug}/#comments"
        )
