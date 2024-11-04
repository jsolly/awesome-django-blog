from django.db import migrations


def copy_date_posted_to_date_updated(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.filter(date_updated__isnull=True):
        post.date_updated = post.date_posted
        post.save()


class Migration(migrations.Migration):
    dependencies = [
        (
            "blog",
            "0039_add_date_updated_to_Post",
        )
    ]

    operations = [
        migrations.RunPython(copy_date_posted_to_date_updated),
    ]
