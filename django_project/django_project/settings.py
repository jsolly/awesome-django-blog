"""
Django settings for django_project project.
Generated by 'django-admin startproject' using Django 2.1.
For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os
from dotenv import load_dotenv
load_dotenv()

GIT_TOKEN = os.environ["GIT_TOKEN"]
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]
SITE_ID = 1  # blogthedata.com
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
CAPTCHA_TEST_MODE = False
USE_SRI = True

# HTTPS SETTINGS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS SETTINGS
SECURE_HSTS_SECONDS = 31557600
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'none'",)
CSP_STYLE_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ('*')
CSP_FRAME_ANCESTORS = ("'none'")
CSP_MANIFEST_SRC = ("'self'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = ("'self'", "https://blogthedata.us14.list-manage.com")
CSP_OBJECT_SRC = ("'none'")
# CSP_REQUIRE_TRUSTED_TYPES_FOR = ("'script'",) # breaks ckeditor
if os.environ["DEBUG"] == "True":
    SITE_ID = 2
    DEBUG = True
    CAPTCHA_TEST_MODE = True

    # HTTPS SETTINGS
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_HTTPONLY = False
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_TYPE_NOSNIFF = False
    CSRF_COOKIE_HTTPONLY = True

    # HSTS SETTINGS
    SECURE_HSTS_SECONDS = 31557600
    SECURE_HSTS_PRELOAD = False
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False


ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(' ')
# Application definition

INSTALLED_APPS = [
    "blog.apps.BlogConfig",
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "captcha",
    "ckeditor",
    "ckeditor_uploader",
    "admin_honeypot",
    "robots",
    "django_fastdev",
    "sri"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.utils.deprecation.MiddlewareMixin",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "csp.middleware.CSPMiddleware"
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "blogthedata",
        "USER": "postgres",
        "PASSWORD": os.environ["POSTGRES_PASS"],
        "HOST": "localhost",
        "PORT": "5432",
    }
}

if os.environ["MODE"] in ('TEST', 'GITACTIONS'):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles"), ]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CKEDITOR_UPLOAD_PATH = "uploads/"

LOGIN_REDIRECT_URL = "blog-home"
LOGIN_URL = "login"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = os.environ["FROM_EMAIL"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# -----FASTDEV-----
FASTDEV_STRICT_IF = True

CKEDITOR_CONFIGS = {
    "default": {
        "removePlugins": "exportpdf",
        # name - Toolbar name
        # items - The buttons enabled in the toolbar
        "toolbar_DefaultToolbarConfig": [
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    "Subscript",
                    "Superscript",
                    "RemoveFormat",
                ],
            },
            {
                "name": "clipboard",
                "items": [
                    "Undo",
                    "Redo",
                ],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "Outdent",
                    "Indent",
                    "HorizontalRule",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                ],
            },
            {
                "name": "links",
                "items": [
                    "Link",
                    "Unlink",
                ],
            },
            {
                "name": "extra",
                "items": [
                    "Blockquote",
                    "Image",
                    "Table",
                    "CodeSnippet",
                ],
            },
            {
                "name": "source",
                "items": [
                    "Maximize",
                    "Source",
                ],
            },
            {
                "name": "styles",
                "items": ["Styles", "Format", "Font", "FontSize"],
            },
            {"name": "colors", "items": ["TextColor", "BGColor"]},
        ],
        # This hides the default title provided by CKEditor
        "title": False,
        # Use this toolbar
        "toolbar": "DefaultToolbarConfig",
        # Which tags to allow in format tab
        "format_tags": "p;h1;h2;h3;h4;h5;h6",
        # Remove these dialog tabs (semicolon separated dialog:tab)
        "removeDialogTabs": ";".join(
            [
                "image:advanced",
                "image:Link",
                "table:advanced",
                "tableProperties:advanced",
            ]
        ),
        "linkShowTargetTab": True,
        "linkShowAdvancedTab": False,
        "allowedContent": True,
        # CKEditor height and width settings
        "height": "400px",
        "width": "auto",
        "forcePasteAsPlainText ": True,
        # Tab = 4 spaces inside the editor
        "tabSpaces": 4,
        # Extra plugins to be used in the editor
        "extraPlugins": ",".join(
            [
                "codesnippet",
                "wordcount",
                "notification",
                "prism"
            ]
        ),
        "codeSnippetGeshi_url": '../lib/colorize.php',
        # Character count
        "wordcount": {
            "showWordCount": False,
            "showCharCount": True,
            "showParagraphs": False,
            "countSpacesAsChars": True,
            "countHTML": True,
            "countLineBreaks": True,
        },
    }
}
