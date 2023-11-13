# Local application/library specific imports
from .base import SetUp
from blog.validators import snippet_validator

# Third-party Imports
from django.core.exceptions import ValidationError


class TestValidators(SetUp):
    def test_snippet_validation(self):
        max_length = 400
        valid_value_with_links = " ".join(
            [f'<a href="http://example{i}.com">Link{i}</a>' for i in range(100)]
        )
        invalid_value = f"""A {'<a href="http://example.com">Link</a> ' * 10}{'B' * (max_length - 10)}"""

        with self.assertRaises(ValidationError):
            snippet_validator(invalid_value, max_length=max_length)

        self.assertTrue(
            snippet_validator(valid_value_with_links, max_length=max_length)
        )
