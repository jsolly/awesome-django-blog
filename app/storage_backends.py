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


class CKEditor5StorageBase:
    """Base mixin for CKEditor storage to ensure consistent path handling"""
    def get_upload_path(self, filename):
        return f"django_ckeditor_5/{filename}"


class CKEditor5StorageS3(CKEditor5StorageBase, S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False

    def _save(self, name, content):
        name = self.get_upload_path(name)
        return super()._save(name, content)


class CKEditor5StorageLocal(CKEditor5StorageBase, FileSystemStorage):
    location = settings.MEDIA_ROOT
    base_url = settings.MEDIA_URL

    def _save(self, name, content):
        name = self.get_upload_path(name)
        return super()._save(name, content)
