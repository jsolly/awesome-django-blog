from .base_settings import *
import sys

USE_SRI = False

# HTTPS SETTINGS
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Check if the `livereload` command is in the command-line arguments
if 'livereload' in sys.argv:
    INSTALLED_APPS += ["livereload"]
    MIDDLEWARE += ["livereload.middleware.LiveReloadScript"]