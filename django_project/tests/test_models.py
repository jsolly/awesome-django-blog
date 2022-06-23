from .base import SetUp
from django.urls import reverse
from PIL import Image
from blog.models import Post, Category
from users.models import Profile
from siteanalytics.models import Visitor
from django.contrib.gis.geos import Point


class TestModels(SetUp):
    def test_post_manager_all(self):
        posts = Post.objects.all()
        self.assertIsInstance(posts[0], Post)
        post_count = posts.count()
        Post.objects.create(
            title="My Second Post",
            slug="second-post",
            category=self.category1,
            metadesc="Curious about your health? Look no further!!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.super_user,
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
            category=self.category1,
            metadesc="Curious about your health? Look no further!!",
            draft=False,
            # metaimg = ""
            # metaimg_mimetype = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            # date_posted = ""
            author=self.super_user,
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
        Category.objects.create(name="TEST")
        self.assertEqual(self.category1.get_absolute_url(), "/category/TEST/")

    def test_post(self):
        self.assertEqual(str(self.post1), f"My First Post | {self.super_user.username}")
        self.assertEqual(self.post1.get_absolute_url(), "/post/first-post/")

        post_no_slug = Post.objects.create(
            title="No slug given",
            # slug="first-post",
            category=self.category1,
            metadesc="Curious about your health? Look no further!",
            draft=False,
            # metaimg = ""
            snippet="Long ago, the four nations lived together in harmony.",
            content="Long ago, the four nations lived together in harmony. Then everything changed when the fire nation attacked.",
            author=self.super_user,
        )
        self.assertEqual(post_no_slug.slug, "no-slug-given")

    # Users Models
    def test_profile(self):
        profile1 = Profile.objects.get(user=self.super_user)
        self.assertEqual(str(profile1), f"{self.super_user.username} Profile")
        self.assertEqual(profile1.get_absolute_url(), reverse("profile"))
        width, height = 400, 400
        img = Image.new(mode="RGB", size=(width, height))
        img.save(profile1.image.path)
        profile1.save()
        with Image.open(profile1.image.path) as img:
            self.assertEqual(img.height, 300)
            self.assertEqual(img.width, 300)

    # SiteAnalytics Models
    def test_visitor(self):
        current_visitors = Visitor.objects.count()
        ip = "156.74.181.208"
        visitor = Visitor.objects.create(
            ip_addr=ip,
            country="United States",
            city="Seattle",
            location=Point(-122.333, 47.604, srid=4326),
        )
        self.assertEqual(str(visitor), ip)
        self.assertGreater(Visitor.objects.count(), current_visitors)
        self.assertIsInstance(Visitor.objects.all()[0], Visitor)