from .base_settings import *

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "blogthedata_test",
        "USER": "dummy-user",
        "PASSWORD": "dummy-password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
