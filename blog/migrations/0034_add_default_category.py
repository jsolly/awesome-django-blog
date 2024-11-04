from django.db import migrations


def create_default_category(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    name = "Uncategorized"
    slug = "uncategorized"
    try:
        Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        Category.objects.create(name=name, slug=slug, description="Default category")


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0033_comment_date_updated"),
    ]

    operations = [
        migrations.RunPython(create_default_category),
    ]
