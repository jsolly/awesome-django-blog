from django.core.management.base import BaseCommand
import json
from blog.models import Post, Category


class Command(BaseCommand):
    help = "Load a list of posts from a JSON file into the Post model"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="The JSON file to load")

    def handle(self, *args, **kwargs):
        json_file = kwargs["json_file"]
        with open(json_file, "r") as f:
            posts_json = json.load(f)

        for post_data in posts_json:
            category = Category.objects.get(slug=post_data["category_slug"])

            post = Post(
                title=post_data["title"],
                content=post_data["content"],
                author_id=post_data["user_id"],
                category=category,
            )
            post.save()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported posts from {json_file}")
        )
