from .base_settings import *
import os
import psycopg2

SITE_ID = 1  # blogthedata.com
CAPTCHA_TEST_MODE = False
X_FRAME_OPTIONS = "SAMEORIGIN"
USE_SRI = False

# HTTPS SETTINGS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# HSTS SETTINGS (Configured in CloudFlare)
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "blogthedata",
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASS"],
        "HOST": "localhost",
        "PORT": "5432",
        "OPTIONS": {
            "isolation_level": psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
        },
    }
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = os.environ["FROM_EMAIL"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
