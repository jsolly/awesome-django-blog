from .base_settings import *
import os

SITE_ID = 2  # localhost
CAPTCHA_TEST_MODE = True
USE_SRI = False

# HTTPS SETTINGS
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

if os.environ["DEBUG"] == "True":
    DEBUG = True
    CSP_SCRIPT_SRC_ELEM += ("http://127.0.0.1:35729/livereload.js",)
    CSP_SCRIPT_SRC += ("http://127.0.0.1:35729/livereload.js",)
    CSP_CONNECT_SRC += ("ws://127.0.0.1:35729/livereload",)


DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "blogthedata",
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASS"],
        "HOST": "localhost",
        "PORT": "5432",
    }
}
