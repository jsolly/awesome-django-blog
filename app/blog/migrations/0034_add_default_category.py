from django.db import migrations
from django.utils.text import slugify


def create_default_category(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    name = "Uncategorized"
    slug = slugify(name)
    Category.objects.create(name=name, slug=slug, description="Default category")


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0033_comment_date_updated"),
    ]

    operations = [
        migrations.RunPython(create_default_category),
    ]
