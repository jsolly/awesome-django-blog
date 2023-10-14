from django.contrib.syndication.views import Feed
from .models import Post
from django.utils.feedgenerator import Atom1Feed


class blogFeed(Feed):
    title = "blogthedata | Blog"
    link = "/rss/"
    description = "Latest blog posts from blogthedata"

    def items(self):
        return Post.objects.active().order_by("-date_updated")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.metadesc


class atomFeed(blogFeed):
    link = "/atom/"
    feed_type = Atom1Feed
    subtitle = blogFeed.description

    def item_author_name(self, item):
        return item.author.username

    def item_updateddate(self, item):
        return item.date_posted
