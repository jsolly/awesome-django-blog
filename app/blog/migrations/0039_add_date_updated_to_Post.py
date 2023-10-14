from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0038_add_default_first_post_and_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="date_updated",
            field=models.DateTimeField(null=True),  # Temporarily allow null values
        ),
    ]
