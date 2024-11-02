from pathlib import Path
import os
import sys
from psycopg import IsolationLevel
import logging

logger = logging.getLogger("django")

if "DYNO" not in os.environ:
    from dotenv import load_dotenv

    load_dotenv()

X_FRAME_OPTIONS = "SAMEORIGIN"
USE_SRI = False

# HTTPS SETTINGS
if str(os.environ.get("DEBUG")).lower() == "false":
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

    # HSTS SETTINGS (Configured in CloudFlare)
    # SECURE_HSTS_SECONDS = 60
    # SECURE_HSTS_PRELOAD = True
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.environ.get("FROM_EMAIL", "")
    DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


BASE_DIR = Path(__file__).resolve().parent.parent  # Three levels up
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = ["*"]
# ALLOWED_HOSTS = []
# ALLOWED_HOSTS.extend(
#     filter(
#         None,
#         os.environ.get("ALLOWED_HOSTS", "").split(" "),
#     )
# )

SITE_ID = int(os.environ["SITE_ID"])

if str(os.environ.get("USE_SQLITE")).lower() == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

else:
    try:
        DATABASES = {
            "default": {
                "ENGINE": os.environ["DB_ENGINE"],
                "NAME": os.environ["DB_NAME"],
                "USER": os.environ["DB_USER"],
                "PASSWORD": os.environ["DB_PASS"],
                "HOST": os.environ["DB_HOST"],
                "PORT": os.environ["DB_PORT"],
                "OPTIONS": {"isolation_level": IsolationLevel.READ_COMMITTED},
            }
        }
    except KeyError:
        message = """
        Please set the following environment variables:
        DB_ENGINE, DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT
        """
        logger.error(message)
        sys.exit(1)


BUCKET_URL = os.environ.get("AWS_URL")

# Content Security Policy
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", BUCKET_URL)
CSP_SCRIPT_SRC_ELEM = ("'self'", "'unsafe-inline'", BUCKET_URL)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'", "'unsafe-inline'", BUCKET_URL)
CSP_MEDIA_SRC = "'self'"
CSP_IMG_SRC = ("'self'", "data:", "*.openstreetmap.org", BUCKET_URL)
CSP_FONT_SRC = "'self'"
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("*",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = "'self'"
CSP_OBJECT_SRC = ("'self'",)
CSP_WORKER_SRC = ("'self'", "blob:")
CSP_EXCLUDE_URL_PREFIXES = "/admin"

DEBUG = False

if str(os.environ.get("DEBUG")).lower() == "true":
    DEBUG = True
    # CSP_SCRIPT_SRC_ELEM += ("http://127.0.0.1:35729/livereload.js",)
    # CSP_SCRIPT_SRC += ("http://127.0.0.1:35729/livereload.js",)
    # CSP_CONNECT_SRC += ("ws://127.0.0.1:35729/livereload",)

INSTALLED_APPS = [
    "blog.apps.BlogConfig",
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.redirects",
    "django_ckeditor_5",
    "robots",
    "sri",
    "django_htmx",
    "django.contrib.humanize",
    "django.contrib.staticfiles",
    "storages",
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
    "csp.middleware.CSPMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

# LiveReload configuration
if str(os.environ.get("LIVERELOAD")).lower() == "true":
    INSTALLED_APPS += ["livereload"]
    MIDDLEWARE += ["livereload.middleware.LiveReloadScript"]


ROOT_URLCONF = "app.urls"

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
                "blog.context_processors.category_renderer",
                "blog.context_processors.breadcrumbs",
            ],
            "debug": True,
        },
    }
]

WSGI_APPLICATION = "app.wsgi.application"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

FORMATTERS = (
    {
        "verbose": {
            "format": "{levelname} {asctime:s} {name} {threadName} {thread:d} {module} {filename} {lineno:d} {name} {funcName} {process:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime:s} {name} {module} {filename} {lineno:d} {funcName} {message}",
            "style": "{",
        },
    },
)


HANDLERS = {
    "console_handler": {
        "class": "logging.StreamHandler",
        "formatter": "simple",
        "level": "DEBUG",
    },
    "info_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": BASE_DIR / "logs/blogthedata_info.log",
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "verbose",
        "level": "INFO",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "error_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": BASE_DIR / "logs/blogthedata_error.log",
        "mode": "a",
        "formatter": "verbose",
        "level": "WARNING",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "ezra_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": BASE_DIR / "logs/ezra.log",
        "mode": "a",
        "formatter": "simple",
        "level": "INFO",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
}

LOGGERS = (
    {
        "django": {
            "handlers": ["console_handler", "info_handler"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["error_handler"],
            "level": "INFO",
            "propagate": True,
        },
        "django.template": {
            "handlers": ["error_handler"],
            "level": "INFO",  # Change to DEBUG to see missing template vars errors
            "propagate": True,
        },
        "django.server": {
            "handlers": ["error_handler"],
            "level": "INFO",
            "propagate": True,
        },
        "ezra_logger": {
            "handlers": ["ezra_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS[0],
    "handlers": HANDLERS,
    "loggers": LOGGERS[0],
}


if os.environ["LOGGING"] == "False":
    LOGGING = None

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

if str(os.environ.get("USE_S3")).lower() == "true":
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    STATIC_LOCATION = "static"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"

    MEDIA_LOCATION = "media"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"

    PRIVATE_MEDIA_LOCATION = "private"

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "app.storage_backends.StaticStorage",
        },
    }

    STATICFILES_STORAGE = "app.storage_backends.StaticStorage"

    DEFAULT_FILE_STORAGE = "app.storage_backends.PublicMediaStorage"
    PRIVATE_FILE_STORAGE = "app.storage_backends.PrivateMediaStorage"

    if str(os.environ.get("USE_S3")).lower() == "true":
        POST_IMAGE_STORAGE = "app.storage_backends.PostImageStorageS3"
    else:
        POST_IMAGE_STORAGE = "app.storage_backends.PostImageStorageLocal"

    CKEDITOR_5_FILE_STORAGE = POST_IMAGE_STORAGE

else:
    STATIC_URL = "/staticfiles/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_LOCATION = "mediafiles"
    MEDIA_URL = "/mediafiles/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    POST_IMAGE_STORAGE = "app.storage_backends.PostImageStorageLocal"
    CKEDITOR_5_FILE_STORAGE = POST_IMAGE_STORAGE


LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# -----FASTDEV-----
# FASTDEV_STRICT_IF = True

customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
            "RemoveFormat",
        ],
    },
    "extends": {
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
            ]
        },
        "link": {"addTargetToExternalLinks": "true"},
        "mediaEmbed": {"previewsInData": "true"},
        "codeBlock": {
            "languages": [
                {"language": "python", "label": "Python"},
                {"language": "css", "label": "CSS"},
                {"language": "yaml", "label": "YAML"},
                {"language": "json", "label": "JSON"},
                {"language": "git", "label": "Git"},
                {"language": "sql", "label": "SQL"},
                {"language": "html", "label": "HTML"},
                {"language": "bash", "label": "BASH"},
                {"language": "javascript", "label": "JavaScript"},
                {"language": "typescript", "label": "TypeScript"},
                {"language": "apacheconf", "label": "ApacheConf"},
            ]
        },
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
            "imageUpload",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "alignment",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageInsert",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}


CKEDITOR_5_CUSTOM_CSS = STATIC_URL + "django_ckeditor_5/ckeditor_custom.css"
