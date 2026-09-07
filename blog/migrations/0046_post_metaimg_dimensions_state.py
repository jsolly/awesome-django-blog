from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0045_post_metaimg_dimensions"),
    ]

    operations = [
        # 0045 creates and backfills the columns while the old model is still
        # safe to run.  This state-only step makes them available to the
        # consumer model in the following release without touching the DB.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="post",
                    name="metaimg_height",
                    field=models.PositiveIntegerField(
                        blank=True, editable=False, null=True
                    ),
                ),
                migrations.AddField(
                    model_name="post",
                    name="metaimg_width",
                    field=models.PositiveIntegerField(
                        blank=True, editable=False, null=True
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
