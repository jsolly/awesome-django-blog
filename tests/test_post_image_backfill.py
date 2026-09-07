from importlib import import_module
from io import BytesIO
from types import SimpleNamespace

from blog.templatetags.image_utils import image_dimension_attrs

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from django.db import connection, migrations
from PIL import Image

from .base import SetUp
from .utils import create_unique_post


def image_upload(name, size):
    image_data = BytesIO()
    Image.new("RGB", size).save(image_data, format="PNG")
    return SimpleUploadedFile(
        name=name,
        content=image_data.getvalue(),
        content_type="image/png",
    )


def dimensions_for(post_id):
    table = connection.ops.quote_name("blog_post")
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT metaimg_width, metaimg_height FROM {table} WHERE id = %s",
            [post_id],
        )
        return cursor.fetchone()


class PostImageBackfillTests(SetUp):
    def test_consumer_migration_changes_state_without_database_operations(self):
        migration = import_module(
            "blog.migrations.0046_post_metaimg_dimensions_state"
        ).Migration
        operation = migration.operations[0]
        self.assertEqual(operation.database_operations, [])
        self.assertEqual(
            {field.name for field in operation.state_operations},
            {"metaimg_width", "metaimg_height"},
        )
        self.assertTrue(
            all(isinstance(field, migrations.AddField) and field.field.null
                for field in operation.state_operations)
        )

    def test_schema_migration_only_adds_nullable_columns(self):
        migration = import_module(
            "blog.migrations.0045_post_metaimg_dimensions"
        ).Migration
        database_operations = migration.operations[0].database_operations

        self.assertEqual(migration.operations[0].state_operations, [])
        self.assertTrue(all(operation.field.null for operation in database_operations))
        self.assertTrue(
            all(isinstance(operation, migrations.AddField) for operation in database_operations)
        )
        self.assertEqual(
            {operation.name for operation in database_operations},
            {"metaimg_width", "metaimg_height"},
        )

    def test_template_uses_actual_dimensions_for_custom_default_filename(self):
        image = SimpleNamespace(
            name="post_metaimgs/default.webp", width=1920, height=640,
            instance=SimpleNamespace(metaimg_width=1920, metaimg_height=640),
        )
        self.assertEqual(image_dimension_attrs(image), 'width="1920" height="640"')
        self.assertEqual(
            image_dimension_attrs(SimpleNamespace(name="default.webp")),
            'width="1207" height="1392"',
        )

    def test_backfill_populates_default_dimensions_without_storage_read(self):
        post = create_unique_post()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE blog_post SET metaimg_width = NULL, metaimg_height = NULL "
                "WHERE id = %s",
                [post.pk],
            )
        self.assertIsNone(dimensions_for(post.pk)[0])

        call_command("backfill_post_image_dimensions")

        self.assertEqual(dimensions_for(post.pk), (1207, 1392))

    def test_backfill_validates_every_image_before_writing_any_row(self):
        valid_post = create_unique_post()
        valid_post.metaimg = image_upload("backfill-valid.png", (3000, 1000))
        valid_post.save()
        image_storage = valid_post._meta.get_field("metaimg").storage
        valid_name = valid_post.metaimg.name
        self.addCleanup(lambda: image_storage.delete(valid_name))

        missing_post = create_unique_post()
        table = connection.ops.quote_name("blog_post")
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {table} SET metaimg_width = NULL, metaimg_height = NULL "
                "WHERE id IN (%s, %s)",
                [valid_post.pk, missing_post.pk],
            )
            cursor.execute(
                f"UPDATE {table} SET metaimg = %s WHERE id = %s",
                ["post_metaimgs/does-not-exist.webp", missing_post.pk],
            )

        with self.assertRaises(CommandError):
            call_command("backfill_post_image_dimensions")

        self.assertEqual(dimensions_for(valid_post.pk), (None, None))
        self.assertEqual(dimensions_for(missing_post.pk), (None, None))

    def test_backfill_does_not_treat_custom_default_named_upload_as_static(self):
        post = create_unique_post()
        post.metaimg = image_upload("default.webp", (3000, 1000))
        post.save()
        image_storage = post._meta.get_field("metaimg").storage
        image_name = post.metaimg.name
        self.addCleanup(lambda: image_storage.delete(image_name))

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE blog_post SET metaimg_width = NULL, metaimg_height = NULL "
                "WHERE id = %s",
                [post.pk],
            )

        call_command("backfill_post_image_dimensions")

        self.assertEqual(dimensions_for(post.pk), (1920, 640))

    def test_backfill_rejects_an_image_changed_after_validation(self):
        post = create_unique_post()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE blog_post SET metaimg_width = NULL, metaimg_height = NULL "
                "WHERE id = %s",
                [post.pk],
            )
        command = import_module(
            "blog.management.commands.backfill_post_image_dimensions"
        ).Command()
        rows = command._load_rows(connection, force=False)
        validated = [
            (row, *command._dimensions_for(row.name))
            for row in rows
            if row.pk == post.pk
        ]

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE blog_post SET metaimg = %s WHERE id = %s",
                ["post_metaimgs/changed.webp", post.pk],
            )

        with self.assertRaises(CommandError):
            command._write_rows(connection, "default", validated)

        self.assertEqual(dimensions_for(post.pk), (None, None))

    def test_force_backfill_reconciles_old_runtime_image_replacement(self):
        post = create_unique_post()
        call_command("backfill_post_image_dimensions", force=True)
        original_dimensions = dimensions_for(post.pk)
        storage = post._meta.get_field("metaimg").storage
        replacement_name = storage.save(
            "post_metaimgs/old-runtime-replacement.png",
            image_upload("replacement.png", (640, 320)),
        )
        self.addCleanup(lambda: storage.delete(replacement_name))
        # The Stage1 model can replace the image without updating new columns.
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE blog_post SET metaimg = %s WHERE id = %s",
                [replacement_name, post.pk],
            )

        call_command("backfill_post_image_dimensions")
        self.assertEqual(dimensions_for(post.pk), original_dimensions)
        call_command("backfill_post_image_dimensions", force=True)
        self.assertEqual(dimensions_for(post.pk), (640, 320))
