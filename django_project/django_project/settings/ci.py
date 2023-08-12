from .base_settings import *

USE_SRI = False

# HTTPS SETTINGS
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
