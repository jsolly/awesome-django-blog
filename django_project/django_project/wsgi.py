import os
from dotenv import load_dotenv

load_dotenv("/home/jsolly/blogthedata/.env")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings.prod")

application = get_wsgi_application()
