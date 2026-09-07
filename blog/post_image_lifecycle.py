from dataclasses import dataclass

from .image_dimensions import DEFAULT_METAIMG_DIMENSIONS, is_default_metaimg

_DIMENSION_FIELDS = frozenset({"metaimg_width", "metaimg_height"})


@dataclass(frozen=True)
class ImageSavePlan:
    """Decisions made before persisting a Post image change."""

    image_name: str
    persisted_name: str
    update_fields: frozenset[str] | None
    effective_update_fields: frozenset[str] | None
    image_was_uploaded: bool
    image_was_cleared: bool
    default_dimensions_need_refresh: bool
    image_was_persisted: bool
    owns_new_storage_object: bool


@dataclass
class ImageCleanupState:
    """Track a newly written storage path while the DB save is in flight."""

    persisted_name: str
    owns_new_storage_object: bool
    name: str | None = None

    def record(self, image_name):
        candidate = owned_image_name(
            self.persisted_name, self.owns_new_storage_object, image_name
        )
        if candidate:
            self.name = candidate


def build_image_save_plan(post, update_fields):
    """Describe image and dimension work for one ``Post.save()`` call."""
    update_fields_set = frozenset(update_fields) if update_fields is not None else None
    image_field = post.metaimg
    image_name = image_field.name if image_field else ""
    persisted_name = getattr(post, "_metaimg_saved_name", "") or ""
    image_name_changed = (
        hasattr(post, "_metaimg_saved_name") and persisted_name != image_name
    )
    image_had_pending_content = bool(image_field and not image_field._committed)
    direct_fieldfile_save_pending = bool(
        getattr(post, "_metaimg_direct_save_pending", False)
    )
    image_was_uploaded = bool(image_field) and (
        image_name_changed
        or image_had_pending_content
        or direct_fieldfile_save_pending
        or (
            post._state.adding
            and bool(image_field)
            and not is_default_metaimg(image_name)
        )
    )
    if image_was_uploaded and update_fields_set is not None:
        image_was_uploaded = "metaimg" in update_fields_set

    image_was_persisted = update_fields_set is None or "metaimg" in update_fields_set
    image_was_cleared = (
        image_was_persisted
        and not image_field
        and (post.metaimg_width is not None or post.metaimg_height is not None)
    )

    default_dimensions_need_refresh = (
        image_was_persisted
        and bool(image_field)
        and is_default_metaimg(image_name)
        and (post.metaimg_width, post.metaimg_height) != DEFAULT_METAIMG_DIMENSIONS
    )

    # Assigning the database default path is a replacement with a known static
    # file. A pending upload named ``default.webp`` is measured after resizing.
    default_path_assignment = (
        image_name_changed
        and bool(image_field)
        and not image_had_pending_content
        and is_default_metaimg(image_name)
    )
    if default_path_assignment and image_was_persisted:
        image_was_uploaded = False
        default_dimensions_need_refresh = True

    dimensions_need_write = (
        image_was_uploaded or image_was_cleared or default_dimensions_need_refresh
    )
    effective_update_fields = update_fields_set
    if dimensions_need_write and effective_update_fields is not None:
        effective_update_fields |= _DIMENSION_FIELDS

    return ImageSavePlan(
        image_name=image_name,
        persisted_name=persisted_name,
        update_fields=update_fields_set,
        effective_update_fields=effective_update_fields,
        image_was_uploaded=image_was_uploaded,
        image_was_cleared=image_was_cleared,
        default_dimensions_need_refresh=default_dimensions_need_refresh,
        image_was_persisted=image_was_persisted,
        owns_new_storage_object=(
            image_had_pending_content or direct_fieldfile_save_pending
        ),
    )


def apply_dimension_state(post, plan):
    """Prepare persisted dimensions before the model save."""
    if plan.image_was_uploaded or plan.image_was_cleared:
        post.metaimg_width = None
        post.metaimg_height = None
    elif plan.default_dimensions_need_refresh:
        post.metaimg_width, post.metaimg_height = DEFAULT_METAIMG_DIMENSIONS


def read_resized_dimensions(image_field):
    """Read dimensions from the stored, transformed image exactly once."""
    image_field._file = None
    image_field.__dict__.pop("_dimensions_cache", None)
    try:
        width, height = image_field.width, image_field.height
        if not width or not height or width <= 0 or height <= 0:
            raise ValueError("stored image has no positive intrinsic dimensions")
        return width, height
    except (OSError, ValueError) as exc:
        raise ValueError(
            f"Unable to read dimensions for saved post image {image_field.name!r}"
        ) from exc


def owned_image_name(persisted_name, owns_new_storage_object, image_name):
    """Return an uploaded path safe to delete after a failed save."""
    if owns_new_storage_object and image_name and image_name != persisted_name:
        return image_name
    return None
