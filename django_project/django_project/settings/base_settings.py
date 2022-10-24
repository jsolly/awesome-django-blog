import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__ + "/../")))
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(" ")
# Content Security Policy
CSP_DEFAULT_SRC = ("'none'",)
CSP_STYLE_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
    "https://api.mapbox.com",
    "'unsafe-inline'",
)
CSP_SCRIPT_SRC_ELEM = (
    "'self'",
    "https://unpkg.com",
    "https://cdn.jsdelivr.net",
    "https://api.mapbox.com",
    "'unsafe-inline'",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://unpkg.com/",
    "https://cdn.jsdelivr.net",
    "https://api.mapbox.com",
)
CSP_MEDIA_SRC = "'self'"
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://unpkg.com/",
    "*.openstreetmap.org",
    "https://storage.ko-fi.com",
    "https://github-readme-twitter",
)
CSP_FONT_SRC = "'self'"
CSP_CONNECT_SRC = (
    "'self'",
    "https://demotiles.maplibre.org/",
    "https://api.mapbox.com",
    "https://events.mapbox.com",
)
CSP_FRAME_SRC = ("*",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = ("'self'", "https://blogthedata.us14.list-manage.com")
CSP_OBJECT_SRC = ("'self'",)
CSP_WORKER_SRC = ("'self'", "blob:")
CSP_EXCLUDE_URL_PREFIXES = ("/admin", "/category/portfolio", "/site-analytics")
# CSP_REQUIRE_TRUSTED_TYPES_FOR = ("'script'",)

DEBUG = False
if os.environ["DEBUG"] == "True":
    DEBUG = True
    CSP_SCRIPT_SRC_ELEM += ("http://127.0.0.1:35729/livereload.js",)
    CSP_SCRIPT_SRC += ("http://127.0.0.1:35729/livereload.js",)
    CSP_CONNECT_SRC += ("ws://127.0.0.1:35729/livereload",)


INSTALLED_APPS = [
    "blog.apps.BlogConfig",
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "livereload",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.redirects",
    "django.contrib.gis",
    "captcha",
    "django_ckeditor_5",
    "robots",
    "sri",
    "siteanalytics",
    "django_htmx",
]

MIDDLEWARE = [
    "siteanalytics.middleware.requestTrackMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.utils.deprecation.MiddlewareMixin",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "csp.middleware.CSPMiddleware",
    "livereload.middleware.LiveReloadScript",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
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
                "blog.custom_context_processor.category_renderer",
            ],
            "debug": True,
        },
    }
]

WSGI_APPLICATION = "django_project.wsgi.application"


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
        "filename": f"{BASE_DIR}/logs/blogthedata_info.log",
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "verbose",
        "level": "INFO",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "error_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/blogthedata_error.log",
        "mode": "a",
        "formatter": "verbose",
        "level": "WARNING",
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
            "level": "DEBUG",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["error_handler"],
            "level": "INFO",
            "propagate": True,
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
USE_L10N = True
USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

# Extra places for collectstatic to find static files.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CKEDITOR_UPLOAD_PATH = "uploads/"

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


CKEDITOR_5_FILE_STORAGE = "blog.storage.CustomStorage"
CKEDITOR_5_CUSTOM_CSS = os.path.join(
    STATIC_URL, "django_ckeditor_5/ckeditor_custom.css"
)
