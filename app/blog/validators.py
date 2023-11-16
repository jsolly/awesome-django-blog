import re
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup

link_media_regex = re.compile(
    r"<a\s[^>]*>.*?</a>|<img\s[^>]*>.*?</img>|<video\s[^>]*>.*?</video>|<audio\s[^>]*>.*?</audio>"
)


def snippet_validator(value, max_length=400):
    # Use BeautifulSoup to parse HTML and extract text content
    soup = BeautifulSoup(value, "html.parser")
    plain_text = soup.get_text(strip=True)
    plain_text_without_links = link_media_regex.sub("", plain_text)
    print(plain_text_without_links)

    # Check the length of the plain text
    if len(plain_text_without_links) > max_length:
        raise ValidationError(
            f"The snippet cannot have more than {max_length} characters (excluding links and media)."
        )

    return True
