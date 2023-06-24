from pathlib import Path
import sys
import os
import json
import psycopg
from django.core.wsgi import get_wsgi_application
from blog.models import Category
from django.contrib.auth.models import User


BASE_DIR = Path(__file__).resolve().parents[2]
django_project_path = BASE_DIR / "django_project"
sys.path.append(str(django_project_path))
os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings.dev"

application = get_wsgi_application()

# Database connection details
db_config = {
    "dbname": "blogthedata",
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASS"],
    "host": "localhost",
    "port": "5432",
}


def fetch_posts(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT title, slug, category_id, metadesc, draft, metaimg, metaimg_alt_txt, metaimg_attribution, content, snippet, date_posted, author_id FROM blog_post"
        )
        return cur.fetchall()


def write_post_to_json(post, export_dir):
    post_dict = {
        "title": post["title"],
        "slug": post["slug"],
        "category": Category.objects.get(id=post["category_id"]).name,
        "metadesc": post["metadesc"],
        "draft": post["draft"],
        "metaimg": post["metaimg"],
        "metaimg_alt_txt": post["metaimg_alt_txt"],
        "metaimg_attribution": post["metaimg_attribution"],
        "content": post["content"],
        "snippet": post["snippet"],
        "date_posted": str(post["date_posted"]),
        "author": User.objects.get(id=post["author_id"]).username,
    }
    filename = f"{post['slug']}.json"
    filepath = export_dir / filename
    with filepath.open("w") as f:
        json.dump(post_dict, f)


def main():
    with psycopg.connect(**db_config) as conn:
        posts = fetch_posts(conn)
        export_dir = BASE_DIR / "utilities/create_embeddings/exported_posts"
        for post in posts:
            write_post_to_json(post, export_dir)


if __name__ == "__main__":
    main()
