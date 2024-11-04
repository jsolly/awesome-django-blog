# Local application/library specific imports
from .base import SetUp
from blog.validators import snippet_validator

# Third-party Imports
from django.core.exceptions import ValidationError


class TestValidators(SetUp):
    def test_snippet_validation_valid_with_links(self):
        max_length = 400
        valid_value_with_links = " ".join(
            [f'<a href="http://example{i}.com">Link</a>' for i in range(100)]
        )

        self.assertTrue(
            snippet_validator(valid_value_with_links, max_length=max_length)
        )

    def test_snippet_validation_valid_formatted_text(self):
        invalid_value = """<p><span style="background-color:rgb(255,255,255);color:rgba(0,0,0,0.9);"><span style="-webkit-text-stroke-width:0px;display:inline !important;float:none;font-family:-apple-system, system-ui, &quot;system-ui&quot;, &quot;Segoe UI&quot;, Roboto, &quot;Helvetica Neue&quot;, &quot;Fira Sans&quot;, Ubuntu, Oxygen, &quot;Oxygen Sans&quot;, Cantarell, &quot;Droid Sans&quot;, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, &quot;Segoe UI Emoji&quot;, &quot;Segoe UI Symbol&quot;, &quot;Lucida Grande&quot;, Helvetica, Arial, sans-serif;font-size:14px;font-style:normal;font-variant-caps:normal;font-variant-ligatures:normal;font-weight:400;letter-spacing:normal;orphans:2;text-align:start;text-decoration-color:initial;text-decoration-style:initial;text-decoration-thickness:initial;text-indent:0px;text-transform:none;white-space:normal;widows:2;word-spacing:0px;">Kick-start your career in geospatial sciences with our Remote Sensing Internship Program! Dive into hands-on projects, learn from industry experts, and make your mark on real-world applications. Apply now and shape the future of remote sensing!</span></span></p>"""

        self.assertTrue(snippet_validator(invalid_value, max_length=400))

    def test_snippet_validation_long_text_exceeding_max_length(self):
        max_length = 400
        long_text = (
            "Lorem ipsum dolor sit amet, "
            "[Link](http://example.com) "
            "![Image](image.jpg) "
            "*emphasis* "
            "**strong** " * 30
        )
        with self.assertRaises(ValidationError):
            snippet_validator(long_text, max_length=max_length)

    def test_snippet_validation_within_max_length(self):
        max_length = 400
        short_text = (
            "Short text within the max length "
            "[Link](http://example.com) "
            "![Image](image.jpg) "
            "*emphasis* "
            "**strong**"
        )
        self.assertTrue(snippet_validator(short_text, max_length=max_length))
