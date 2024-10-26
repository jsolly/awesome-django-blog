from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage
from urllib.parse import urljoin


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"
    file_overwrite = True  # Set to False if you don't want to overwrite existing files


class PublicMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = "private"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False


class CKEditor5StorageS3(S3Boto3Storage):
    location = "media/django_ckeditor_5"
    default_acl = "public-read"
    file_overwrite = False

    def url(self, name):
        return f"{settings.MEDIA_URL}django_ckeditor_5/{name}"


class CKEditor5StorageLocal(FileSystemStorage):
    location = "media/django_ckeditor_5"
    base_url = urljoin(settings.MEDIA_URL, "django_ckeditor_5/")
