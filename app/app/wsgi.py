import os
from django.core.wsgi import get_wsgi_application

# Set the DJANGO_SETTINGS_MODULE environment variable before calling get_wsgi_application
os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings.notreal"

# Print it for debugging
print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"))

# Load the application
application = get_wsgi_application()
