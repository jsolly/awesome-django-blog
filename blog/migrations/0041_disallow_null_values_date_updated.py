from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "blog",
            "0040_populate_date_updated_with_date_posted",
        )
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="date_updated",
            field=models.DateTimeField(
                auto_now=True, null=False
            ),  # Now disallow null values
        ),
    ]
