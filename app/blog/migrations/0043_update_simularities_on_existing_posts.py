from django.db import migrations
from blog.utils import compute_similarity


def update_similarity(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all():
        compute_similarity(post.id)


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0042_add_simularity_model"),
    ]

    operations = [
        migrations.RunPython(update_similarity),
    ]
