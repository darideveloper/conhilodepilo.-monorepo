import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env first to get ENV value
load_dotenv(BASE_DIR / ".env")
ENV = os.getenv("ENV", "dev")

# Load environment-specific file
load_dotenv(BASE_DIR / f".env.{ENV}")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

from urllib.parse import urlparse

HOST = os.getenv("HOST", "")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

if HOST:
    host_name = urlparse(HOST).hostname
    if host_name and host_name not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host_name)

print(f"DEBUG: {DEBUG}")
print(f"ENV: {ENV}")

# Application definition

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "solo",
    "storages",
    "booking",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "project" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "project.context_processors.brand_theme_context",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
IS_TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

if IS_TESTING:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "testing.sqlite3"),
        }
    }
else:
    options = {}
    if os.environ.get("DB_ENGINE") == "django.db.backends.mysql":
        options = {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        }

    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("DB_NAME", os.path.join(BASE_DIR, "db.sqlite3")),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", ""),
            "OPTIONS": options,
        }
    }


# Password validation
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
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Mexico_City")
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("es", _("Spanish")),
    ("en", _("English")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Core Identity
COMPANY_NAME = os.getenv("COMPANY_NAME")

# Integrations
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")


# Static & Media Management
STATIC_URL = "static/"
MEDIA_URL = "/media/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STORAGE_AWS = os.getenv("STORAGE_AWS") == "True"
print(f"STORAGE_AWS: {STORAGE_AWS}")

if STORAGE_AWS:
    # 1. Credentials
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    # 2. Regional Settings
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

    # 3. Domain/CDN settings
    AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")

    # 4. Folder isolation
    AWS_PROJECT_FOLDER = os.getenv("AWS_PROJECT_FOLDER")

    # 5. File Locations
    STATIC_LOCATION = f"{AWS_PROJECT_FOLDER}/static"
    PUBLIC_MEDIA_LOCATION = f"{AWS_PROJECT_FOLDER}/media"
    PRIVATE_MEDIA_LOCATION = f"{AWS_PROJECT_FOLDER}/private"

    # 6. Django-Storages Engine Mapping
    STORAGES = {
        "default": {
            "BACKEND": "project.storage_backends.PublicMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "project.storage_backends.StaticStorage",
        },
        "private": {
            "BACKEND": "project.storage_backends.PrivateMediaStorage",
        },
    }

    # 7. Optimization & Security
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_DEFAULT_ACL = None
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# CORS & CSRF Configuration
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") == "True"

cors_allowed = os.getenv("CORS_ALLOWED_ORIGINS")
if cors_allowed and cors_allowed != "None":
    CORS_ALLOWED_ORIGINS = [
        origin.strip().rstrip("/")
        for origin in cors_allowed.split(",")
        if origin.strip()
    ]

csrf_trusted = os.getenv("CSRF_TRUSTED_ORIGINS")
if csrf_trusted and csrf_trusted != "None":
    CSRF_TRUSTED_ORIGINS = [
        origin.strip().rstrip("/")
        for origin in csrf_trusted.split(",")
        if origin.strip()
    ]

# Django REST Framework Setup
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "project.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "EXCEPTION_HANDLER": "project.handlers.custom_exception_handler",
}

# Global DateTime Formatting
DATE_FORMAT = "d/b/Y"
TIME_FORMAT = "H:i"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

# Email SMTP Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL") == "True"
EMAIL_FROM = EMAIL_HOST_USER
EMAILS_NOTIFICATIONS = os.getenv("EMAILS_NOTIFICATIONS", "").split(",")

# Unfold Settings
UNFOLD = {
    "SITE_TITLE": "utils.callbacks.site_title_callback",
    "SITE_HEADER": "utils.callbacks.site_header_callback",
    "SITE_SUBHEADER": _("Dashboard"),
    "SITE_URL": "/",
    "SITE_ICON": "utils.callbacks.site_icon_callback",
    # "SITE_LOGO": "utils.callbacks.site_icon_callback",
    "SITE_SYMBOL": "directions_car",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("favicon.png"),
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "utils.callbacks.environment_callback",
    "THEME": "light",
    "COLORS": {
        "primary": {
            "50": "var(--brand-primary-50, oklch(0.97 0.02 296))",
            "100": "var(--brand-primary-100, oklch(0.92 0.04 296))",
            "200": "var(--brand-primary-200, oklch(0.85 0.08 296))",
            "300": "var(--brand-primary-300, oklch(0.75 0.15 296))",
            "400": "var(--brand-primary-400, oklch(0.70 0.22 296))",
            "500": "var(--brand-primary-500, oklch(0.68 0.28 296))",
            "600": "var(--brand-primary-600, oklch(0.60 0.25 296))",
            "700": "var(--brand-primary-700, oklch(0.50 0.20 296))",
            "800": "var(--brand-primary-800, oklch(0.40 0.16 296))",
            "900": "var(--brand-primary-900, oklch(0.30 0.12 296))",
            "950": "var(--brand-primary-950, oklch(0.20 0.08 296))",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Management"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Bookings"),
                        "icon": "event",
                        "link": reverse_lazy("admin:booking_booking_changelist"),
                    },
                    {
                        "title": _("Services"),
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:booking_event_changelist"),
                    },
                ],
            },
            {
                "title": _("Configuration"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Company Profile"),
                        "icon": "business",
                        "link": reverse_lazy("admin:booking_companyprofile_changelist"),
                    },
                ],
            },
            {
                "title": _("Authentication"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
