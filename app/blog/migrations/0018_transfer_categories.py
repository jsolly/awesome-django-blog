# Generated by Django 3.2.13 on 2022-06-01 14:35

from django.db import migrations


def link_categories(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    Category = apps.get_model("blog", "Category")
    for post in Post.objects.all():
        category, created = Category.objects.get_or_create(name=post.category)
        post.category_link = category
        post.save()


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0017_add_temp_category_link_field"),
    ]

    operations = [migrations.RunPython(link_categories)]
