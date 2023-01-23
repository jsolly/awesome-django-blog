from django import template
import readtime
import html

register = template.Library()


def read(input_html):
    clean_html = html.escape(input_html)
    return readtime.of_html(clean_html)


register.filter("readtime", read)
