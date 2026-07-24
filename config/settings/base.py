import os
from pathlib import Path
from datetime import timedelta

from config.settings.app_config import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config.app.secret_key


AUTH_USER_MODEL = "accounts.UserModel"

AUTHENTICATION_BACKENDS = [
    "authentication.backends.AuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# ---------------------------------------------------------------
# Installed Apps Configuration
# ---------------------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party apps
    "corsheaders",
    "django_filters",
    "rest_framework",
    "django_cleanup.apps.CleanupSelectedConfig",
    # Custom apps
    "accounts",
    "authentication",
    "finance",
]

# ---------------------------------------------------------------
# Middleware Configuration
# ---------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------
# URL Configuration
# ---------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------
# Password Validation
# ---------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------
LANGUAGE_CODE = config.i18n.language_code

TIME_ZONE = config.i18n.time_zone

USE_I18N = config.i18n.use_i18n

USE_TZ = config.i18n.use_tz


# ---------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = config.cors.allow_credentials
CORS_ALLOWED_ORIGINS = config.cors.allowed_origins
CSRF_TRUSTED_ORIGINS = config.cors.trusted_origins

INTERNAL_IPS = config.cors.internal_ips
ALLOWED_HOSTS = config.cors.allowed_hosts


# ---------------------------------------------------------------
# Email Configuration
# ---------------------------------------------------------------
EMAIL_BACKEND = config.email.backend
EMAIL_HOST = config.email.host
EMAIL_PORT = config.email.port
EMAIL_USE_TLS = config.email.use_tls
EMAIL_USE_SSL = config.email.use_ssl
EMAIL_HOST_USER = config.email.host_user
EMAIL_HOST_PASSWORD = config.email.host_password
DEFAULT_FROM_EMAIL = config.email.default_from_email

# ---------------------------------------------------------------
# Celery Configuration
# ---------------------------------------------------------------
CELERY_BROKER_URL = config.celery.broker_url
CELERY_RESULT_BACKEND = config.celery.result_backend
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = config.i18n.time_zone

# ---------------------------------------------------------------
# Simple JWT Configuration
# ---------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=config.auth.access_token_lifetime),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config.auth.refresh_token_lifetime),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": True,
}


# ---------------------------------------------------------------
# Logging Configuration (FIXED)
# ---------------------------------------------------------------

# LOG_DIR = BASE_DIR / "logs"
# LOG_DIR.mkdir(parents=True, exist_ok=True)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{asctime}] [{levelname}] [{name}] {message}",
            "style": "{",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
