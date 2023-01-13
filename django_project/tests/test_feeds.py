from .base import SetUp, create_several_posts
from blog.feeds import blogFeed, atomFeed
from django.urls import resolve, reverse
import feedparser


class TestFeeds(SetUp):
    def test_blog_feed_url_is_resolved(self):
        self.assertTrue(isinstance(resolve(reverse("rss")).func, blogFeed))

    def test_atom_feed_url_is_resolved(self):
        self.assertTrue(isinstance(resolve(reverse("atom")).func, atomFeed))

    def test_feed_metadata(self):
        response = self.client.get("/rss/")
        feed = feedparser.parse(response.content)
        self.assertEqual(feed.feed.title, "blogthedata | Blog")
        self.assertEqual(feed.feed.description, "Latest blog posts from blogthedata")

    def test_rss_feed_items(self):
        create_several_posts(self.category1, self.super_user, 20)
        response = self.client.get("/rss/")
        feed = feedparser.parse(response.content)
        self.assertEqual(len(feed.entries), 5)

    def test_atom_feed_items(self):
        create_several_posts(self.category1, self.super_user, 20)
        response = self.client.get("/atom/")
        feed = feedparser.parse(response.content)
        self.assertEqual(len(feed.entries), 5)
