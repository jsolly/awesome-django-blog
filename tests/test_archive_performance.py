from html.parser import HTMLParser
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from PIL import Image

from .base import SetUp
from .utils import create_unique_post

from blog.image_dimensions import DEFAULT_METAIMG_DIMENSIONS
from blog.models import Post


def image_upload(name, size):
    image_data = BytesIO()
    Image.new("RGB", size).save(image_data, format="PNG")
    return SimpleUploadedFile(
        name=name,
        content=image_data.getvalue(),
        content_type="image/png",
    )


class MetaPropertyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.properties = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attributes = dict(attrs)
        property_name = attributes.get("property")
        if property_name:
            self.properties[property_name] = attributes.get("content")


class ArchivePerformanceTests(SetUp):
    def test_persisted_dimensions_are_not_author_editable_fields(self):
        self.assertFalse(Post._meta.get_field("metaimg_width").editable)
        self.assertFalse(Post._meta.get_field("metaimg_height").editable)

    def test_archive_query_count_is_bounded_and_rendering_never_opens_media(self):
        create_unique_post()

        def render_archive():
            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(reverse("all-posts"))
            return response, len(queries)

        image_storage = Post._meta.get_field("metaimg").storage
        with patch.object(
            image_storage,
            "open",
            side_effect=AssertionError("archive rendering opened post media"),
        ):
            baseline_response, baseline_queries = render_archive()
            for _ in range(5):
                create_unique_post()
            expanded_response, expanded_queries = render_archive()

        self.assertEqual(baseline_response.status_code, 200)
        self.assertEqual(expanded_response.status_code, 200)
        self.assertLessEqual(expanded_queries, baseline_queries + 1)
        self.assertLessEqual(expanded_queries, 4)

        html = expanded_response.content.decode()
        for post in Post.objects.filter(draft=False):
            self.assertIn(f'href="{post.get_absolute_url()}"', html)
        self.assertNotIn(self.draft_post.get_absolute_url(), html)

    def test_post_detail_uses_persisted_dimensions_without_opening_media(self):
        post = create_unique_post()
        image_storage = Post._meta.get_field("metaimg").storage

        with patch.object(
            image_storage,
            "open",
            side_effect=AssertionError("post detail opened post media"),
        ):
            response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        meta_properties = MetaPropertyParser()
        meta_properties.feed(html)
        self.assertEqual(meta_properties.properties["og:image:width"], "1207")
        self.assertEqual(meta_properties.properties["og:image:height"], "1392")

    def test_post_detail_omits_missing_custom_dimensions_without_storage_read(self):
        post = create_unique_post()
        image_storage = Post._meta.get_field("metaimg").storage
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE blog_post SET metaimg = %s, metaimg_width = NULL, "
                "metaimg_height = NULL WHERE id = %s",
                ["post_metaimgs/missing-custom.webp", post.pk],
            )

        with patch.object(
            image_storage,
            "open",
            side_effect=AssertionError("missing dimensions opened post media"),
        ):
            response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        meta_properties = MetaPropertyParser()
        meta_properties.feed(html)
        self.assertNotIn("og:image:width", meta_properties.properties)
        self.assertNotIn("og:image:height", meta_properties.properties)
        image_start = html.index('id="post-detail-meta-img"')
        image_end = html.index(">", image_start)
        self.assertNotIn("width=", html[image_start:image_end])

    def test_uploaded_and_replaced_images_store_resized_dimensions(self):
        post = create_unique_post()
        image_storage = Post._meta.get_field("metaimg").storage
        uploaded_names = []
        self.addCleanup(lambda: [image_storage.delete(name) for name in uploaded_names])

        post.metaimg = image_upload("archive-wide.png", (3000, 1000))
        # Form validation can inspect the source image before Model.save().
        self.assertEqual((post.metaimg.width, post.metaimg.height), (3000, 1000))
        post.save()
        self.assertEqual((post.metaimg_width, post.metaimg_height), (1920, 640))
        uploaded_names.append(post.metaimg.name)

        post.metaimg = image_upload("archive-tall.png", (800, 2000))
        post.save(update_fields=["metaimg"])
        post.refresh_from_db()
        self.assertEqual((post.metaimg_width, post.metaimg_height), (432, 1080))
        uploaded_names.append(post.metaimg.name)

        # Reassigning an already-stored image still refreshes dimensions; it
        # must not preserve the dimensions of the previous upload.
        post.metaimg = uploaded_names[0]
        post.save(update_fields=["metaimg"])
        post.refresh_from_db()
        self.assertEqual((post.metaimg_width, post.metaimg_height), (1920, 640))

        post.metaimg = "default.webp"
        with patch.object(
            image_storage,
            "open",
            side_effect=AssertionError("default replacement should not read storage"),
        ):
            post.save(update_fields=["metaimg"])
        post.refresh_from_db()
        self.assertEqual(
            (post.metaimg_width, post.metaimg_height), DEFAULT_METAIMG_DIMENSIONS
        )

        post.metaimg = image_upload("default.webp", (3000, 1000))
        post.save(update_fields=["metaimg"])
        post.refresh_from_db()
        self.assertEqual((post.metaimg_width, post.metaimg_height), (1920, 640))
        uploaded_names.append(post.metaimg.name)

    def test_direct_fieldfile_save_updates_dimensions_on_fresh_instance(self):
        post = create_unique_post()
        post = Post.objects.get(pk=post.pk)
        image_storage = Post._meta.get_field("metaimg").storage
        image = image_upload("direct-fieldfile.png", (3000, 1000))
        self.addCleanup(lambda: image_storage.delete(post.metaimg.name))

        post.metaimg.save(image.name, image, save=True)
        post.refresh_from_db()

        self.assertEqual((post.metaimg_width, post.metaimg_height), (1920, 640))

    def test_direct_fieldfile_save_on_new_post_updates_dimensions(self):
        image_storage = Post._meta.get_field("metaimg").storage
        post = Post(
            title="Direct new fieldfile",
            category=self.default_category,
            author=self.admin_user,
            content="Content",
            snippet="Snippet",
        )
        image = image_upload("direct-new-fieldfile.png", (3000, 1000))

        post.metaimg.save(image.name, image, save=True)
        image_name = post.metaimg.name
        self.addCleanup(lambda: image_storage.delete(image_name))
        post.refresh_from_db()

        self.assertEqual((post.metaimg_width, post.metaimg_height), (1920, 640))

    def test_failed_direct_save_preserves_existing_image_and_cleans_new_file(self):
        post = Post.objects.get(pk=create_unique_post().pk)
        image_storage = Post._meta.get_field("metaimg").storage
        old_name = post.metaimg.name
        old_dimensions = (post.metaimg_width, post.metaimg_height)
        image = image_upload("direct-existing-failure.png", (3000, 1000))
        self.addCleanup(
            lambda: (
                image_storage.delete(post.metaimg.name)
                if post.metaimg.name != old_name
                else None
            )
        )

        with (
            patch.object(
                image_storage,
                "open",
                side_effect=OSError("dimension read failed"),
            ),
            self.assertRaises(ValueError),
        ):
            post.metaimg.save(image.name, image, save=True)

        new_name = post.metaimg.name
        self.assertNotEqual(new_name, old_name)
        self.assertFalse(image_storage.exists(new_name))
        persisted = Post.objects.get(pk=post.pk)
        self.assertEqual(persisted.metaimg.name, old_name)
        self.assertEqual(
            (persisted.metaimg_width, persisted.metaimg_height), old_dimensions
        )

    def test_post_save_failure_cleans_existing_direct_replacement(self):
        post = Post.objects.get(pk=create_unique_post().pk)
        image_storage = Post._meta.get_field("metaimg").storage
        old_name = post.metaimg.name
        old_dimensions = (post.metaimg_width, post.metaimg_height)
        image = image_upload("direct-post-save-failure.png", (3000, 1000))
        self.addCleanup(
            lambda: (
                image_storage.delete(post.metaimg.name)
                if post.metaimg.name != old_name
                else None
            )
        )

        with (
            patch(
                "blog.signals.compute_similarity",
                side_effect=RuntimeError("post-save failure"),
            ),
            self.assertRaises(RuntimeError),
        ):
            post.metaimg.save(image.name, image, save=True)

        new_name = post.metaimg.name
        self.assertNotEqual(new_name, old_name)
        self.assertFalse(image_storage.exists(new_name))
        persisted = Post.objects.get(pk=post.pk)
        self.assertEqual(persisted.metaimg.name, old_name)
        self.assertEqual(
            (persisted.metaimg_width, persisted.metaimg_height), old_dimensions
        )

    def test_direct_fieldfile_save_false_then_model_save_updates_dimensions(self):
        image_storage = Post._meta.get_field("metaimg").storage
        post = Post(
            title="Direct deferred fieldfile",
            category=self.default_category,
            author=self.admin_user,
            content="Content",
            snippet="Snippet",
        )
        image = image_upload("direct-save-false.png", (800, 2000))

        post.metaimg.save(image.name, image, save=False)
        post.save()
        image_name = post.metaimg.name
        self.addCleanup(lambda: image_storage.delete(image_name))
        post.refresh_from_db()

        self.assertEqual((post.metaimg_width, post.metaimg_height), (432, 1080))

    def test_deferred_image_baseline_and_partial_save_do_not_stale_dimensions(self):
        source = create_unique_post()
        image_storage = Post._meta.get_field("metaimg").storage
        source.metaimg = image_upload("deferred-source.png", (3000, 1000))
        source.save()
        source_name = source.metaimg.name
        self.addCleanup(lambda: image_storage.delete(source_name))

        target = create_unique_post()
        deferred = Post.objects.only(
            "id", "title", "metaimg_width", "metaimg_height"
        ).get(pk=target.pk)

        # Saving a deferred instance without update_fields makes Django save
        # only its loaded columns.  The image remains deferred and its
        # persisted-name marker must stay absent until the image is saved.
        deferred.title = "Deferred partial title"
        deferred.save()
        self.assertFalse(hasattr(deferred, "_metaimg_saved_name"))

        deferred.metaimg = source_name

        deferred.save(update_fields=["title"])
        target.refresh_from_db()
        self.assertEqual(target.metaimg.name, "default.webp")
        self.assertEqual(
            (target.metaimg_width, target.metaimg_height), DEFAULT_METAIMG_DIMENSIONS
        )

        deferred.save()
        target.refresh_from_db()
        self.assertEqual(target.metaimg.name, source_name)
        self.assertEqual((target.metaimg_width, target.metaimg_height), (1920, 640))

    def test_dimension_only_save_does_not_reconcile_unpersisted_image_assignment(self):
        post = create_unique_post()
        image_storage = Post._meta.get_field("metaimg").storage
        post.metaimg = image_upload("dimension-only-source.png", (3000, 1000))
        post.save()
        image_name = post.metaimg.name
        self.addCleanup(lambda: image_storage.delete(image_name))
        post.refresh_from_db()
        original_dimensions = (post.metaimg_width, post.metaimg_height)

        post.metaimg = "default.webp"
        post.save(update_fields=["metaimg_width"])
        persisted = Post.objects.get(pk=post.pk)
        self.assertEqual(persisted.metaimg.name, image_name)
        self.assertEqual(
            (persisted.metaimg_width, persisted.metaimg_height), original_dimensions
        )

        post.refresh_from_db()
        post.metaimg = None
        post.save(update_fields=["metaimg_width"])
        persisted.refresh_from_db()
        self.assertEqual(persisted.metaimg.name, image_name)
        self.assertEqual(
            (persisted.metaimg_width, persisted.metaimg_height), original_dimensions
        )

    def test_failed_dimension_read_rolls_back_new_row_and_cleans_uploaded_file(self):
        image_storage = Post._meta.get_field("metaimg").storage
        post = Post(
            title="Atomic image failure",
            category=self.default_category,
            author=self.admin_user,
            content="Content",
            snippet="Snippet",
            metaimg=image_upload("atomic-failure.png", (3000, 1000)),
        )

        with (
            patch.object(
                image_storage,
                "open",
                side_effect=OSError("dimension read failed"),
            ),
            self.assertRaises(ValueError),
        ):
            post.save()

        self.assertIsNone(post.pk)
        self.assertTrue(post._state.adding)
        self.assertFalse(Post.objects.filter(title="Atomic image failure").exists())
        self.assertFalse(image_storage.exists(post.metaimg.name))

    def test_empty_stored_image_dimensions_roll_back_and_clean_upload(self):
        image_storage = Post._meta.get_field("metaimg").storage
        post = Post(
            title="Empty stored image",
            category=self.default_category,
            author=self.admin_user,
            content="Content",
            snippet="Snippet",
            metaimg=image_upload("empty-stored-image.png", (640, 320)),
        )
        with (
            patch.object(image_storage, "open", return_value=BytesIO(b"")),
            self.assertRaises(ValueError),
        ):
            post.save()

        self.assertIsNone(post.pk)
        self.assertFalse(Post.objects.filter(title="Empty stored image").exists())
        self.assertFalse(image_storage.exists(post.metaimg.name))

    def test_invalid_pending_upload_named_existing_object_does_not_delete_it(self):
        image_storage = Post._meta.get_field("metaimg").storage
        post = create_unique_post()
        post.refresh_from_db()
        old_name = post.metaimg.name
        old_dimensions = (post.metaimg_width, post.metaimg_height)
        self.assertEqual(old_name, "default.webp")
        self.assertTrue(image_storage.exists(old_name))

        post.metaimg = SimpleUploadedFile(
            old_name,
            b"not an image",
            content_type="image/webp",
        )
        with self.assertRaises(OSError):
            post.save()

        persisted = Post.objects.get(pk=post.pk)
        self.assertEqual(persisted.metaimg.name, old_name)
        self.assertEqual(
            (persisted.metaimg_width, persisted.metaimg_height), old_dimensions
        )
        self.assertTrue(image_storage.exists(old_name))
