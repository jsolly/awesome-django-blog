from dataclasses import dataclass

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from PIL import Image, UnidentifiedImageError

from blog.image_dimensions import DEFAULT_METAIMG_DIMENSIONS, is_default_metaimg
from blog.models import Post


@dataclass(frozen=True)
class ImageRow:
    pk: int
    slug: str | None
    name: str
    width: int | None
    height: int | None


class Command(BaseCommand):
    help = (
        "Populate Post.metaimg_width/metaimg_height from the stored, resized "
        "post images. Run after migration 0045 and before the consumer release. "
        "Missing media or concurrent image changes fail the command."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help=f"Database to use (default: {DEFAULT_DB_ALIAS}).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recompute dimensions for every post instead of only missing rows.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Read and validate dimensions without writing the database.",
        )

    def handle(self, *args, **options):
        database_alias = options["database"]
        connection = connections[database_alias]
        rows = self._load_rows(connection, force=options["force"])
        validated = []
        missing = []

        # Read and validate every object before opening a transaction or issuing
        # an UPDATE.  A bad object therefore cannot leave a partially-filled
        # dimensions table behind.
        for row in rows:
            try:
                width, height = self._dimensions_for(row.name)
            except (OSError, ValueError, UnidentifiedImageError) as exc:
                missing.append(
                    f"pk={row.pk} slug={row.slug!r} image={row.name!r}: {exc}"
                )
                continue

            validated.append((row, width, height))

        if missing:
            preview = "; ".join(missing[:10])
            if len(missing) > 10:
                preview += f"; … and {len(missing) - 10} more"
            raise CommandError(
                f"Could not read dimensions for {len(missing)} post image(s): "
                f"{preview}"
            )

        if options["dry_run"]:
            self.stdout.write(f"Validated {len(validated)} post image dimension row(s).")
            return

        updated = self._write_rows(connection, database_alias, validated)
        self.stdout.write(f"Updated {updated} post image dimension row(s).")

    @staticmethod
    def _load_rows(connection, *, force):
        """Read only columns present before the consumer model release.

        This command intentionally does not use ``metaimg_width`` or
        ``metaimg_height`` as Django model fields.  The schema-only release
        runs it while the application still has the old ``Post`` model.
        """

        meta = Post._meta
        table = connection.ops.quote_name(meta.db_table)
        pk_column = connection.ops.quote_name(meta.pk.column)
        slug_column = connection.ops.quote_name(meta.get_field("slug").column)
        image_column = connection.ops.quote_name(meta.get_field("metaimg").column)
        width_column = connection.ops.quote_name("metaimg_width")
        height_column = connection.ops.quote_name("metaimg_height")
        where = ""
        if not force:
            where = f"WHERE {width_column} IS NULL OR {height_column} IS NULL"

        query = (
            f"SELECT {pk_column}, {slug_column}, {image_column}, "
            f"{width_column}, {height_column} FROM {table} {where} "
            f"ORDER BY {pk_column}"
        )
        with connection.cursor() as cursor:
            cursor.execute(query)
            return [ImageRow(*row) for row in cursor.fetchall()]

    @staticmethod
    def _dimensions_for(name):
        if not name:
            raise ValueError("post has no image name")
        # Only the exact database default is trusted.  A custom upload called
        # ``default.webp`` is stored below ``post_metaimgs/`` and is inspected.
        if is_default_metaimg(name):
            return DEFAULT_METAIMG_DIMENSIONS

        storage = Post._meta.get_field("metaimg").storage
        with storage.open(name, "rb") as image_file:
            with Image.open(image_file) as image:
                width, height = image.size
                image.verify()

        if not width or not height:
            raise ValueError("stored image has no intrinsic dimensions")
        return width, height

    @staticmethod
    def _write_rows(connection, database_alias, validated):
        if not validated:
            return 0

        meta = Post._meta
        table = connection.ops.quote_name(meta.db_table)
        pk_column = connection.ops.quote_name(meta.pk.column)
        image_column = connection.ops.quote_name(meta.get_field("metaimg").column)
        width_column = connection.ops.quote_name("metaimg_width")
        height_column = connection.ops.quote_name("metaimg_height")
        query = (
            f"UPDATE {table} SET {width_column} = %s, {height_column} = %s "
            f"WHERE {pk_column} = %s AND {image_column} = %s"
        )

        with transaction.atomic(using=database_alias):
            with connection.cursor() as cursor:
                for row, width, height in validated:
                    cursor.execute(query, (width, height, row.pk, row.name))
                    if cursor.rowcount != 1:
                        raise CommandError(
                            "Post image changed while dimensions were being "
                            f"backfilled (pk={row.pk}, image={row.name!r}); "
                            "rerun the command."
                        )

        return len(validated)
