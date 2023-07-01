from .base import SetUp
from django.urls import reverse
from PIL import Image
from blog.models import Post, Comment, slugify_instance
from users.models import Profile
from .utils import create_user, create_post


class TestModels(SetUp):
    def setUp(self):
        self.test_user = create_user()

    def test_dummy(self):
        self.assertEqual(1, 1)

    def test_slugify_instance(self):
        test_post = create_post()
        slugify_instance(test_post, new_slug="lorem-ipsum-post", save=True)
        self.assertEqual(test_post.slug, "lorem-ipsum-post")

    def test_post_manager_all(self):
        create_post()
        posts = Post.objects.all()
        self.assertIsInstance(posts[0], Post)
        post_count = posts.count()
        create_post()
        new_post_count = Post.objects.count()
        self.assertEqual(new_post_count, post_count + 1)

    def test_post_manager_active(self):
        create_post()
        active_posts = Post.objects.active()
        self.assertIsInstance(active_posts[0], Post)
        active_posts_count = active_posts.count()
        another_post = create_post()
        new_active_post_count = Post.objects.active().count()
        self.assertEqual(new_active_post_count, active_posts_count + 1)
        another_post.draft = True
        another_post.save()
        active_posts_minus_draft = Post.objects.active().count()
        self.assertEqual(active_posts_minus_draft, new_active_post_count - 1)

    def test_category_absolute_url(self):
        self.assertEqual(
            self.test_category.get_absolute_url(),
            f"/category/{self.test_category.slug}/",
        )

    def test_post_absolute_url(self):
        test_post = create_post()
        self.assertEqual(test_post.get_absolute_url(), f"/post/{test_post.slug}/")

    # Users Models
    def test_profile(self):
        profile1 = Profile.objects.get(user=self.test_user)
        self.assertEqual(str(profile1), f"{self.test_user.username} Profile")
        self.assertEqual(profile1.get_absolute_url(), reverse("profile"))
        width, height = 400, 400
        img = Image.new(mode="RGB", size=(width, height))
        img.save(profile1.image.path)
        profile1.save()
        with Image.open(profile1.image.path) as img:
            self.assertEqual(img.height, 300)
            self.assertEqual(img.width, 300)

    def test_create_comment(self):
        test_post = create_post()
        comment = Comment.objects.create(
            post=test_post,
            author=self.test_user,
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        )
        self.assertEqual(comment.post, test_post)
        self.assertEqual(comment.author, self.test_user)
        self.assertEqual(
            comment.content, "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
