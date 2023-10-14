# Third-party Imports
from django.urls import resolve, reverse
import feedparser


# Local application/library specific imports
from .base import SetUp
from blog.feeds import atomFeed, blogFeed


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
        response = self.client.get("/rss/")
        feed = feedparser.parse(response.content)
        self.assertTrue(hasattr(feed.entries[0], "title"))

    def test_atom_feed_items(self):
        response = self.client.get("/atom/")
        feed = feedparser.parse(response.content)
        self.assertTrue(hasattr(feed.entries[0], "title"))
