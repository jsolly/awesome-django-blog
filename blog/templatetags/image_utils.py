from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import re
import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def fix_image_urls(content):
    """
    Takes content with image paths and converts them to full URLs based on storage backend.
    Handles relative paths, full mediafiles paths, and CloudFront URLs.
    
    When USE_CLOUD=True:
        "post_imgs/image.png"                                              → "https://<distrbution_id>.cloudfront.net/media/post_imgs/image.png"
        "/mediafiles/post_imgs/image.png"                                  → "https://<distrbution_id>.cloudfront.net/media/post_imgs/image.png"
        "https://<distrbution_id>.cloudfront.net/media/post_imgs/image.png" → "https://<distrbution_id>.cloudfront.net/media/post_imgs/image.png"
    
    When USE_CLOUD=False:
        "post_imgs/image.png"                                              → "/mediafiles/post_imgs/image.png"
        "/mediafiles/post_imgs/image.png"                                  → "/mediafiles/post_imgs/image.png"
        "https://<distrbution_id>.cloudfront.net/media/post_imgs/image.png" → "/mediafiles/post_imgs/image.png"
    """
    if not content:
        return content

    # Pattern to match all possible formats including full CloudFront URLs
    cloudfront_pattern = re.escape(f"{settings.STATIC_HOST}/{settings.MEDIA_LOCATION}/")
    pattern = r'src="(?:' + cloudfront_pattern + r'|/mediafiles/|https://[^/]+/media/)?((?:post_imgs|uploads)/[^"]*)"'
    
    def replace_url(match):
        # Get the path part without any prefix
        path = match.group(1)
        logger.debug(f"Fixing image URL for path: {path}")
        
        if settings.USE_CLOUD:
            url = f"{settings.STATIC_HOST}/{settings.MEDIA_LOCATION}/{path}"
            logger.debug(f"Using CloudFront URL: {url}")
            return f'src="{url}"'
        else:
            url = f"/mediafiles/{path}"
            logger.debug(f"Using local URL: {url}")
            return f'src="{url}"'
    
    fixed_content = re.sub(pattern, replace_url, content)
    return mark_safe(fixed_content)

@register.simple_tag
def get_image_url(image_field):
    """
    Returns the correct URL for an image field based on storage backend:
    - When USE_CLOUD=True: Use CloudFront URL with /media/
    - When USE_CLOUD=False: Use /mediafiles/
    """
    if not image_field:
        return ""
        
    if settings.USE_CLOUD:
        return f"{settings.STATIC_HOST}/{settings.MEDIA_LOCATION}/{image_field.name}"
    else:
        return f"/mediafiles/{image_field.name}"


# Intrinsic size of static/default.webp (Post.metaimg default) — avoid opening storage.
_DEFAULT_METAIMG_WH = (1207, 1392)


@register.simple_tag
def image_dimension_attrs(image_field, default_width=1200, default_height=630):
    """Return safe width=/height= attributes for CLS without 500ing on missing media."""
    if not image_field:
        return ""
    name = getattr(image_field, "name", "") or ""
    if name.endswith("default.webp"):
        w, h = _DEFAULT_METAIMG_WH
        return mark_safe(f'width="{w}" height="{h}"')
    try:
        w, h = image_field.width, image_field.height
    except (ValueError, OSError) as exc:
        logger.warning("image dimensions unavailable; using defaults (%s)", exc)
        return mark_safe(f'width="{default_width}" height="{default_height}"')
    if w and h:
        return mark_safe(f'width="{w}" height="{h}"')
    return mark_safe(f'width="{default_width}" height="{default_height}"')
