from django.db import migrations
from django.template.defaultfilters import slugify


def create_default_post_and_comment(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    Category = apps.get_model("blog", "Category")
    Comment = apps.get_model("blog", "Comment")
    User = apps.get_model("auth", "User")

    # Get default category
    category = Category.objects.get(slug="uncategorized")

    # Use Admin user
    admin_user = User.objects.get(username="admin")

    # Create a default post
    post = Post.objects.create(
        title="Learn How to Use Awesome Django Blog",
        slug=slugify("Learn How to Use Awesome Django Blog"),
        category=category,
        content="""In this post, you will learn how to use Awesome Django Blog.
        <h2>Login and Edit Your Profile</h2>
        In order to add and edit posts, you need to be logged in. You can login by clicking the
        login button on the top right corner of the page. The default supersuer account is admin and the
        default password is admin. To change your password and profile photo, you can click the
        profile button on the top right corner of the page after you login. When you change your
        profile photo, the image will be stored in awesome-django-blog/media/profile_pics.
        <h2>Create a New Post</h2>
        After you login, you can click the "New Post" button on the top right corner of the page.
        <h2>Upload Images</h2>
        You can upload images by either copy/pasting into the editor or by clicking the image
        button on the toolbar. You can also upload images by dragging and dropping them into the
        editor. The post metaimage will be stored in awesome-django-blog/media/post_metaimgs.
        Any images added to the editor will be stored in awesome-django-blog/media/django_ckeditor_5.
        """,
        snippet="<p>Learn how to use all the features including creating posts, adding comments, and creating your first profile!</p>",
        author=admin_user,
        metaimg_alt_txt="Default Image Alt Text",
    )

    # Create a default comment
    # Use comment_only user
    comment_only_user = User.objects.get(username="comment_only")

    Comment.objects.create(
        post=post,
        author=comment_only_user,
        content="This is an example of a comment. The default comment_only user can only create, update, and delete their own comments, not posts.",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0037_create_default_site"),
    ]

    operations = [
        migrations.RunPython(create_default_post_and_comment),
    ]
