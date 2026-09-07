import html

import readtime
from django import template

register = template.Library()


def read(input_html):
    if not input_html:
        return "0 minutes"

    clean_html = html.escape(input_html)
    return readtime.of_html(clean_html)


register.filter("readtime", read)


@register.filter
def comment_count(post):
    """Use the archive annotation when present, then preserve other cards."""
    annotated_count = getattr(post, "card_comment_count", None)
    if annotated_count is not None:
        return annotated_count
    return post.comments.count()
