from django.db import migrations
from django.contrib.sites.models import Site


def create_default_site(apps, schema_editor):
    Site.objects.get_or_create(name="localhost", domain="localhost:8000")


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0036_add_default_users"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ]
