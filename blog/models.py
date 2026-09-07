import logging

from django.contrib.auth.models import User
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField
from django_resized.forms import ResizedImageFieldFile

from .post_image_lifecycle import (
    ImageCleanupState,
    apply_dimension_state,
    build_image_save_plan,
    read_resized_dimensions,
)

# import logging
# logger = logging.getLogger("django")
logger = logging.getLogger(__name__)


class _PostMetaimgFieldFile(ResizedImageFieldFile):
    """Mark direct FieldFile.save() calls before they save the model."""

    def save(self, name, content, save=True):
        self.instance._metaimg_direct_save_pending = True
        try:
            result = super().save(name, content, save=save)
            cleanup_state = getattr(self.instance, "_metaimg_cleanup_state", None)
            if cleanup_state is not None:
                cleanup_state.record(self.name)
            return result
        except Exception:
            cleanup_state = getattr(self.instance, "_metaimg_cleanup_state", None)
            if cleanup_state is not None and self._committed:
                cleanup_state.record(self.name)
            self.instance._metaimg_direct_save_pending = False
            raise


def slugify_instance(instance, save=False, new_slug=None):
    if new_slug:
        instance.slug = new_slug
    else:
        if isinstance(instance, Post):
            instance.slug = slugify(instance.title)
        elif isinstance(instance, Category):
            instance.slug = slugify(instance.name)

    if save:
        instance.save()


class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        return super().filter(draft=False).order_by("-date_posted")

    def all(self, *args, **kwargs):
        return super().order_by("-date_posted")


class CommentManager(models.Manager):
    def all(self, *args, **kwargs):
        return super().order_by("-date_posted")


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.CharField(max_length=140)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog-category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance(self, save=False)

        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    metadesc = models.CharField(max_length=500, blank=True, null=True)
    draft = models.BooleanField(default=False)
    metaimg = ResizedImageField(
        force_format="WEBP",
        quality=75,
        upload_to="post_metaimgs",
        default="default.webp",
    )
    # Persist the dimensions of the resized file.  Reading ImageField.width or
    # .height for an S3-backed field opens the object, which is too expensive
    # to do once per card on the archive.  These stay nullable until the
    # explicit backfill command has inspected legacy media.
    metaimg_width = models.PositiveIntegerField(
        null=True, blank=True, editable=False
    )
    metaimg_height = models.PositiveIntegerField(
        null=True, blank=True, editable=False
    )
    metaimg_alt_txt = models.CharField(max_length=500, default="John Solly Headshot")
    metaimg_attribution = models.CharField(max_length=500, blank=True, null=True)
    content = CKEditor5Field(blank=True, null=True)
    snippet = CKEditor5Field(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = PostManager()  # Make sure objects only include active (not draft) posts.

    @classmethod
    def from_db(cls, db, field_names, values, *, fetch_mode=None):
        instance = super().from_db(db, field_names, values, fetch_mode=fetch_mode)
        if "metaimg" in field_names:
            instance._metaimg_saved_name = instance.metaimg.name
        return instance

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        super().refresh_from_db(using=using, fields=fields, from_queryset=from_queryset)
        # A partial refresh can leave an assigned deferred image in the
        # instance dictionary even though the database did not refresh it.
        # Only advance the persisted-image baseline when this refresh actually
        # included the image field (or was a full refresh).
        if fields is None or "metaimg" in fields:
            self._metaimg_saved_name = self.metaimg.name

    def get_related_posts(self) -> models.QuerySet:
        """
        Get the top 3 related posts based on the similarities
        """

        return Post.objects.filter(
            id__in=self.similarities1.order_by("-score").values_list(
                "post2", flat=True
            )[:3]
        )

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def _ensure_metaimg_baseline(self, database_alias):
        if (
            not hasattr(self, "_metaimg_saved_name")
            and self.pk is not None
            and not self._state.adding
        ):
            # A deferred field can be assigned a committed path without ever
            # loading its old value. Establish the DB baseline before deciding
            # whether dimensions need to be refreshed.
            self._metaimg_saved_name = (
                self.__class__._base_manager.using(database_alias)
                .filter(pk=self.pk)
                .values_list("metaimg", flat=True)
                .first()
                or ""
            )

    def _delete_owned_image(self, image_name):
        if not image_name:
            return
        try:
            self.metaimg.storage.delete(image_name)
        except Exception:
            logger.exception(
                "Unable to clean up post image after dimension failure",
                extra={"metaimg_name": image_name},
            )

    def _save_uploaded_image(self, args, kwargs, plan, database_alias):
        cleanup_state = ImageCleanupState(
            persisted_name=plan.persisted_name,
            owns_new_storage_object=plan.owns_new_storage_object,
        )
        # Register cleanup before Model.save() so a post_save exception cannot
        # strand a file written by FileField.pre_save().
        self._metaimg_cleanup_state = cleanup_state
        try:
            with transaction.atomic(using=database_alias):
                super().save(*args, **kwargs)
                saved_image = self.metaimg
                cleanup_state.record(saved_image.name)
                width, height = read_resized_dimensions(saved_image)
                self.metaimg_width = width
                self.metaimg_height = height
                # Keep this bookkeeping update out of Model.save()/post_save
                # so an image upload does not trigger similarity computation
                # twice. The image-name predicate prevents a stale upload
                # from writing dimensions over a concurrent change.
                updated = (
                    self.__class__._base_manager.using(database_alias)
                    .filter(pk=self.pk, metaimg=saved_image.name)
                    .update(metaimg_width=width, metaimg_height=height)
                )
                if updated != 1:
                    raise ValueError(
                        "Post image changed while dimensions were being saved "
                        f"(pk={self.pk}, image={saved_image.name!r})"
                    )
        except Exception:
            saved_image = self.__dict__.get("metaimg")
            if getattr(saved_image, "_committed", False):
                cleanup_state.record(saved_image.name)
            self._delete_owned_image(cleanup_state.name)
            raise
        finally:
            if getattr(self, "_metaimg_cleanup_state", None) is cleanup_state:
                del self._metaimg_cleanup_state

    def save(self, *args, **kwargs):
        if not self.slug:
            slugify_instance(self, save=False)

        update_fields = kwargs.get("update_fields")
        update_fields_set = set(update_fields) if update_fields is not None else None
        image_is_deferred = "metaimg" in self.get_deferred_fields()
        if image_is_deferred and (
            update_fields_set is None or "metaimg" not in update_fields_set
        ):
            # Django saves only loaded fields for a deferred instance when
            # update_fields is omitted. Do not fetch the image merely to
            # compare it, and do not advance its baseline marker.
            super().save(*args, **kwargs)
            return

        database_alias = self._state.db or "default"
        self._ensure_metaimg_baseline(database_alias)
        plan = build_image_save_plan(self, update_fields)
        if plan.effective_update_fields is not None:
            kwargs["update_fields"] = set(plan.effective_update_fields)
        apply_dimension_state(self, plan)

        original_state_db = self._state.db
        was_adding = self._state.adding
        try:
            if plan.image_was_uploaded:
                self._save_uploaded_image(args, kwargs, plan, database_alias)
            else:
                super().save(*args, **kwargs)
        except Exception:
            if was_adding and self.pk is not None:
                self.pk = None
                self._state.adding = True
                self._state.db = original_state_db
            raise

        if plan.image_was_persisted:
            self._metaimg_saved_name = self.metaimg.name
            self._metaimg_direct_save_pending = False

    def get_metaimg_url(self):
        if self.metaimg:
            return self.metaimg.url
        return None


# Keep the migration field class unchanged while marking direct file saves for
# the lifecycle bookkeeping above.
Post._meta.get_field("metaimg").attr_class = _PostMetaimgFieldFile


class Similarity(models.Model):
    post1 = models.ForeignKey(
        Post, related_name="similarities1", on_delete=models.CASCADE
    )
    post2 = models.ForeignKey(
        Post, related_name="similarities2", on_delete=models.CASCADE
    )
    score = models.FloatField()

    # Ensure that the same pair of posts can't be added twice
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post1", "post2"], name="unique_pair")
        ]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = CKEditor5Field(blank=True, null=True, config_name="extends")
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = CommentManager()

    class Meta:
        ordering = ["date_posted"]

    def __str__(self):
        return f"Comment '{self.content}' by {self.author}"

    def get_absolute_url(self):
        post_url = reverse("post-detail", kwargs={"slug": self.post.slug})
        comments_section_url = f"{post_url}#comments"
        return comments_section_url
