from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage
from urllib.parse import urljoin


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"
    file_overwrite = True


class PublicMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = "private"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False


class PostImageStorageBase:
    """Base mixin for post image storage to ensure consistent path handling"""
    def get_upload_path(self, filename):
        return f"post_imgs/{filename}"


class PostImageStorageS3(PostImageStorageBase, S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False

    def _save(self, name, content):
        name = self.get_upload_path(name)
        return super()._save(name, content)


class PostImageStorageLocal(PostImageStorageBase, FileSystemStorage):
    location = settings.MEDIA_ROOT
    base_url = settings.MEDIA_URL

    def _save(self, name, content):
        name = self.get_upload_path(name)
        return super()._save(name, content)
