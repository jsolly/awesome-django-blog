import re
from django.core.exceptions import ValidationError

link_media_pattern = re.compile(
    r"<a[^>]*>.*?</a>|<img[^>]*>.*?</img>|<video[^>]*>.*?</video>|<audio[^>]*>.*?</audio>",
    flags=re.IGNORECASE | re.DOTALL,
)


def snippet_validator(value, max_length=400):
    value_without_links_media = link_media_pattern.sub("", value)
    if len(value_without_links_media) > max_length:
        raise ValidationError(
            f"The snippet cannot have more than {max_length} characters (excluding links and media)."
        )
    return True
