from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import re
import os

register = template.Library()

@register.filter
def fix_image_urls(content):
    """
    Takes content with relative image paths and converts them to full URLs based on storage backend.
    Example: 
        Input:  src="post_imgs/image.png"
        Output: src="https://bucket.s3.amazonaws.com/media/post_imgs/image.png" (if USE_S3)
                src="/mediafiles/post_imgs/image.png" (if local storage)
    """
    if not content:
        return content

    # Pattern to match relative image paths
    pattern = r'src="((?:post_imgs|uploads)/[^"]*)"'
    
    def replace_url(match):
        path = match.group(1)
        if os.environ.get("USE_S3") == "True":
            bucket_url = settings.BUCKET_URL.rstrip("/")
            return f'src="{bucket_url}/media/{path}"'
        else:
            return f'src="/mediafiles/{path}"'
    
    return mark_safe(re.sub(pattern, replace_url, content))

@register.simple_tag
def get_image_url(image_field):
    """
    Returns the correct URL for an image field based on storage backend:
    - When USE_S3=True: Use AWS bucket URL with /media/
    - When USE_S3=False: Use /mediafiles/
    """
    if not image_field:
        return ""
        
    file_path = str(image_field.name)
    
    if os.environ.get("USE_S3") == "True":
        bucket_url = settings.BUCKET_URL.rstrip("/")
        return f"{bucket_url}/media/{file_path}"
    else:
        return f"/mediafiles/{file_path}"
