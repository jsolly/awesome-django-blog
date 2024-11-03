from pathlib import Path
import os
import sys
from psycopg import IsolationLevel
import logging

if "DYNO" not in os.environ:
    from dotenv import load_dotenv

    load_dotenv()
    
def get_bool_env(var_name, default=False):
    return str(os.environ.get(var_name, str(default))).lower() == "true"

def get_qualified_hosts():
    qualified_hosts = []
    for host in ALLOWED_HOSTS:
        if host in ('localhost', '127.0.0.1') and DEBUG: # Allow localhost for development
            qualified_hosts.extend([
                    f"http://{host}:8000",
                ])
            continue
            
        # Handle wildcard domains (starting with dot)
        if host.startswith('.'):
            domain = host[1:]
            qualified_hosts.append(f"https://*.{domain}")
        else:
            qualified_hosts.append(f"https://{host}")
    
    return qualified_hosts

DEBUG = get_bool_env("DEBUG", False)
LOGGING = get_bool_env("LOGGING", False)
BASE_DIR = Path(__file__).resolve().parent.parent  # Three levels up
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(" ")
FULLY_QUALIFIED_ALLOWED_HOSTS = get_qualified_hosts()
SITE_ID = int(os.environ["SITE_ID"])
X_FRAME_OPTIONS = "SAMEORIGIN"
USE_SRI = False
USE_CLOUD = get_bool_env("USE_CLOUD")
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_HOST = os.environ.get("DJANGO_STATIC_HOST", "") if USE_CLOUD else ""

logger = logging.getLogger("django")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # CSRF_COOKIE_HTTPONLY = True # Broke ckedtor5 image uploads
    # CSRF_COOKIE_SECURE = True
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

    CSRF_TRUSTED_ORIGINS = FULLY_QUALIFIED_ALLOWED_HOSTS


if get_bool_env("USE_SQLITE"):
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

# Content Security Policy
CSP_SCRIPT_SRC_ELEM = (
    "'self'", 
    "'unsafe-inline'", 
    STATIC_HOST,
)
CSP_SCRIPT_SRC = (
    "'self'", 
    "'unsafe-eval'", 
    "'unsafe-inline'", 
    STATIC_HOST,
)
CSP_CONNECT_SRC = tuple(["'self'"] + FULLY_QUALIFIED_ALLOWED_HOSTS)

# Livereload.js is on 127.0.0.1:35729
# There is never a reason to allow livereload.js in production
if DEBUG and get_bool_env("LIVERELOAD"):
    CSP_SCRIPT_SRC_ELEM += ("http://127.0.0.1:35729",)
    CSP_SCRIPT_SRC += ("http://127.0.0.1:35729",)
    CSP_CONNECT_SRC += ("ws://127.0.0.1:35729",)

CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", STATIC_HOST)
CSP_MEDIA_SRC = "'self'"
CSP_IMG_SRC = tuple(["'self'", "data:", "https://openstreetmap.org", "https://*.openstreetmap.org", STATIC_HOST] +
                    FULLY_QUALIFIED_ALLOWED_HOSTS)
CSP_FONT_SRC = "'self'"
CSP_FRAME_SRC = tuple(["'self'"] + 
                     FULLY_QUALIFIED_ALLOWED_HOSTS +
                     ["https://youtube.com",
                      "https://*.youtube.com",
                      "https://nbviewer.org/",
                      "https://*.nbviewer.org/"])
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = "'self'"
CSP_OBJECT_SRC = ("'self'",)
CSP_WORKER_SRC = ("'self'", "blob:")
CSP_EXCLUDE_URL_PREFIXES = "/admin"

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
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
    # "sri",
    "django_htmx",
    "django.contrib.humanize",
    "django.contrib.staticfiles",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

if get_bool_env("LIVERELOAD"):
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
            "debug": DEBUG,
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

FORMATTERS = {
    "verbose": {
        "format": "{levelname} {asctime:s} {name} {threadName} {thread:d} {module} {filename} {lineno:d} {funcName} {process:d} {message}",
        "style": "{",
    },
    "simple": {
        "format": "{levelname} {asctime:s} {name} {module} {filename} {lineno:d} {funcName} {message}",
        "style": "{",
    },
}


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

LOGGERS = {
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
    "django.core.files": {
        "handlers": ["console_handler"],
        "level": "DEBUG",
        "propagate": True,
    },
    "storages": {
        "handlers": ["console_handler"],
        "level": "DEBUG",
        "propagate": True,
    },
    "app.storage_backends": {
        "handlers": ["console_handler"],
        "level": "DEBUG",
        "propagate": True,
    },
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS,
    "handlers": HANDLERS,
    "loggers": LOGGERS,
}


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

if USE_CLOUD:
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"  # Need this for uploads
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    STATIC_LOCATION = "static"
    STATIC_URL = f"{STATIC_HOST}/{STATIC_LOCATION}/"

    MEDIA_LOCATION = "media"
    MEDIA_URL = f"{STATIC_HOST}/{MEDIA_LOCATION}/"  # This should be used for all media
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

    PRIVATE_MEDIA_LOCATION = "private"

    BUCKET_URL = os.environ.get("AWS_BUCKET_URL")  # Keep this for uploads

    STORAGES = {
        "default": {
            "BACKEND": "app.storage_backends.PublicMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "app.storage_backends.StaticStorage",
        },
        "media": { 
            "BACKEND": "app.storage_backends.PublicMediaStorage",
        }
    }

    PRIVATE_FILE_STORAGE = "app.storage_backends.PrivateMediaStorage"
    POST_IMAGE_STORAGE = "app.storage_backends.PostImageStorageS3"
    CKEDITOR_5_FILE_STORAGE = POST_IMAGE_STORAGE

else:
    STATIC_URL = f"{STATIC_HOST}/staticfiles/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_LOCATION = "mediafiles"
    MEDIA_URL = f"{STATIC_HOST}/mediafiles/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
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
        "simpleUpload": {
            "uploadUrl": "/ckeditor5/image_upload/",
            "withCredentials": True,
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


CKEDITOR_5_CUSTOM_CSS = f"{STATIC_HOST}/django_ckeditor_5/ckeditor_custom.css"
