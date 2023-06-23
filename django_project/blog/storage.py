from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from pathlib import Path


class CustomStorage(FileSystemStorage):
    location = str(Path(settings.MEDIA_ROOT) / "django_ckeditor_5")
    base_url = urljoin(settings.MEDIA_URL, "django_ckeditor_5/")
