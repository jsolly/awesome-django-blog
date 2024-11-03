from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"
    file_overwrite = True

    def url(self, name):
        """Override url method to use CloudFront domain"""
        logger.debug(f"StaticStorage.url called for {name}")
        if settings.USE_CLOUD and settings.STATIC_HOST:
            url = f"{settings.STATIC_HOST}/{self.location}/{name}"
            logger.debug(f"Returning CloudFront URL: {url}")
            return url
        url = super().url(name)
        logger.debug(f"Returning S3 URL: {url}")
        return url


class PublicMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False

    def url(self, name):
        """Override url method to use CloudFront domain"""
        logger.debug(f"PublicMediaStorage.url called for {name}")
        if settings.USE_CLOUD and settings.STATIC_HOST:
            url = f"{settings.STATIC_HOST}/{self.location}/{name}"
            logger.debug(f"Returning CloudFront URL: {url}")
            return url
        url = super().url(name)
        logger.debug(f"Returning S3 URL: {url}")
        return url


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
        logger.debug(f"PostImageStorageS3._save called for {name}")
        name = self.get_upload_path(name)
        logger.debug(f"Saving with path: {name}")
        return super()._save(name, content)

    def url(self, name):
        """Override url method to use CloudFront domain"""
        logger.debug(f"PostImageStorageS3.url called for {name}")
        if settings.USE_CLOUD and settings.STATIC_HOST:
            url = f"{settings.STATIC_HOST}/{self.location}/{self.get_upload_path(name)}"
            logger.debug(f"Returning CloudFront URL: {url}")
            return url
        url = super().url(name)
        logger.debug(f"Returning S3 URL: {url}")
        return url


class PostImageStorageLocal(PostImageStorageBase, FileSystemStorage):
    location = settings.MEDIA_ROOT
    base_url = settings.MEDIA_URL

    def _save(self, name, content):
        name = self.get_upload_path(name)
        return super()._save(name, content)

