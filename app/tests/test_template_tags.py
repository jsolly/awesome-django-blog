# Local application/library specific imports
from blog.templatetags.post_utils import read
from unittest import TestCase


class TestTemplateTags(TestCase):
    def test_html_read_time_no_input(self):
        self.assertEqual(read(""), "0 minutes")
