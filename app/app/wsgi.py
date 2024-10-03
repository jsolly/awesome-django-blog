from django.core.wsgi import get_wsgi_application
import os

print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"))

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings.notreal"
application = get_wsgi_application()
