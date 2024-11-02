from django import template
from django.conf import settings
import os

register = template.Library()


@register.simple_tag
def get_image_url(image_field):
    """
    Returns the correct URL for an image field based on storage backend:
    - When USE_S3=True: Use AWS bucket URL with /media/
    - When USE_S3=False: Use /mediafiles/
    """
    # Get just the filename and path after the media directory
    file_path = str(image_field.name)

    if str(os.environ.get("USE_S3")).lower() == "true":
        bucket_url = settings.BUCKET_URL.rstrip("/")  # Remove trailing slash if present
        return f"{bucket_url}/media/{file_path}"
    else:
        return f"/mediafiles/{file_path}"
