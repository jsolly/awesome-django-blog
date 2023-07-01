# Local application/library specific imports
from .base import SetUp
from blog.templatetags.post_utils import read


class TestTemplateTags(SetUp):
    def test_html_read_time_no_input(self):
        self.assertEqual(read(""), "0 minutes")
