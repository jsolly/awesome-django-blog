from .base_settings import *
import os
import json

SITE_ID = 2  # localhost
CAPTCHA_TEST_MODE = True
USE_SRI = False
DEBUG = False
# HTTPS SETTINGS
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Override the default database with a dummy database
if os.environ.get("CUSTOM_CI_DB_SETTINGS_STRING"):
    db_settings = json.loads(CUSTOM_CI_DB_SETTINGS_STRING)

for key, value in db_settings.items():
    DATABASES["default"][key] = value

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "dummy_db",
            "USER": "dummy_user",
            "PASSWORD": "dummy_password",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
