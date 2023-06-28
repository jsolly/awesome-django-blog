from django import template
import readtime
import html

register = template.Library()


def read(input_html):
    # Check if input_html is None or empty
    if not input_html:
        return "0 minutes"

    clean_html = html.escape(input_html)
    return readtime.of_html(clean_html)


register.filter("readtime", read)
