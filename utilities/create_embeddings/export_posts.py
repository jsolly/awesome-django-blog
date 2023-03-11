import os
import sys
from django.core.wsgi import get_wsgi_application

# This is the blogthedata directory if you cloned the repo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Add the parent directory of the Django project to the system path
django_project_path = os.path.join(BASE_DIR, "django_project")
sys.path.append(django_project_path)

os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings.dev"

# Initialize the Django application
application = get_wsgi_application()

import json
import psycopg2
from psycopg2 import extras
from blog.models import Category
from django.contrib.auth.models import User


# Connect to the database
conn = psycopg2.connect(
    database="blogthedata",
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASS"],
    host="localhost",
    port="5432",
)

# Query the Post table and retrieve all posts
with conn.cursor(cursor_factory=extras.DictCursor) as cur:
    cur.execute(
        "SELECT title, slug, category_id, metadesc, draft, metaimg, metaimg_alt_txt, metaimg_attribution, content, snippet, date_posted, author_id FROM blog_post"
    )
    posts = cur.fetchall()

# Export each post as a separate JSON file
export_dir = os.path.join(BASE_DIR, "utilities/create_embeddings/exported_posts")

for post in posts:
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
    filepath = os.path.join(export_dir, filename)
    with open(filepath, "w") as f:
        json.dump(post_dict, f)

# Close the database connection
conn.close()
