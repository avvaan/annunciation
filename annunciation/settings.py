"""
Django settings for the Annunciation of the Most Holy Theotokos parish site
(Jacksonville, FL).
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-#z^x81@&uap#*j+2-dd0r(&tb(rkslt$pjuiva%($f()agkwwh"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h]
CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

# Render sets this to the service's *.onrender.com hostname; add it automatically
# so ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS don't need to be set by hand for it.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Render terminates TLS at its proxy and talks plain HTTP to the app.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_ckeditor_5",
    "core",
    "services",
    "publications",
    "building",
    "school",
    "history",
    "newsletter",
    "ministries",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "annunciation.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "annunciation.wsgi.application"


# Database
# DATABASE_URL is set automatically by Render when a Postgres instance is
# attached to this service; without it, falls back to local sqlite.

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# Russian is the primary language (unprefixed URLs), English is secondary (/en/...).

LANGUAGE_CODE = "ru"

LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "America/New_York"

USE_I18N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True

# django-modeltranslation: Russian is the source of truth, English falls back to it.
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
MODELTRANSLATION_LANGUAGES = ("ru", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("ru",)
MODELTRANSLATION_CUSTOM_FIELDS = ("CKEditor5Field",)


# Static / media files

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Render's own filesystem is wiped on every deploy/restart — uploaded media
# (schedule/publication PDFs, ministry documents, photos) only survives
# across deploys if this points at a mounted Render Disk. Set
# RENDER_DISK_MOUNT_PATH to that mount path (e.g. "/var/data") once a Disk is
# attached to the service; until then media uploads WILL be lost on redeploy.
_media_root = Path(os.environ.get("RENDER_DISK_MOUNT_PATH", BASE_DIR))

MEDIA_URL = "media/"
MEDIA_ROOT = _media_root / "media"

# Private, non-web-served storage for ministry documents (membership/leader-gated
# downloads only, never served directly by the webserver).
PRIVATE_MEDIA_ROOT = _media_root / "private_media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "ministries:login"
LOGIN_REDIRECT_URL = "ministries:ministry_list"


# django-ckeditor-5

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "link", "bulletedList",
            "numberedList", "blockQuote", "|", "undo", "redo",
        ],
    },
}

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@annunciationjax.org")
