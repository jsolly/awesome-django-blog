from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0044_alter_post_metaimg"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AddField(
                    model_name="post",
                    name="metaimg_height",
                    field=models.PositiveIntegerField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="post",
                    name="metaimg_width",
                    field=models.PositiveIntegerField(blank=True, null=True),
                ),
            ],
            state_operations=[],
        ),
    ]
