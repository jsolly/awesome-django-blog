from django.db import migrations
from django.core.exceptions import ObjectDoesNotExist


def create_default_admin_and_post(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("users", "Profile")

    # Create default admin user
    try:
        admin_user = User.objects.get(username="admin")
    except ObjectDoesNotExist:
        admin_user = User.objects.create_superuser(
            username="admin", password="admin", email="admin@example.com"
        )
        Profile.objects.create(user=admin_user)

    # Create Comment only user
    try:
        comment_only_user = User.objects.get(username="comment_only")
    except ObjectDoesNotExist:
        comment_only_user = User.objects.create_user(
            username="comment_only",
            password="comment_only",
            email="comment_only@example.com",
        )
        Profile.objects.create(user=comment_only_user)


class Migration(migrations.Migration):
    dependencies = [("blog", "0035_change_default_meta_img"), ("users", "0001_initial")]

    operations = [
        migrations.RunPython(create_default_admin_and_post),
    ]
