"""
Application configuration module.

This module loads all environment variables
and provides centralized access to settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass

# Project root (directory containing manage.py and .env)
ROOT_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = ROOT_DIR / ".env"

# print("=" * 60)
# print("Loading .env from:", ENV_FILE)
# print("Exists:", ENV_FILE.exists())

load_dotenv(ENV_FILE, override=True)

# print("CORS_ALLOWED_ORIGINS =", os.getenv("CORS_ALLOWED_ORIGINS"))
# print("=" * 60)


@dataclass(frozen=True)
class AppConfig:
    """
    Application configuration.
    """

    stage: str
    debug: bool
    secret_key: str
    base_url: str
    admin_url: str


@dataclass(frozen=True)
class InternationalizationConfig:
    """
    Internationalization configuration.
    """

    language_code: str
    time_zone: str
    use_i18n: bool
    use_tz: bool


@dataclass(frozen=True)
class EmailConfig:
    """
    Email configuration.
    """

    backend: str
    host: str
    port: int
    use_tls: bool
    use_ssl: bool
    host_user: str
    host_password: str
    default_from_email: str
    max_retry_attempts: int


@dataclass(frozen=True)
class CeleryConfig:
    """
    Celery configuration.
    """

    broker_url: str
    result_backend: str


@dataclass(frozen=True)
class AuthConfig:
    """
    Authentication configuration.
    """

    otp_length: int
    otp_ttl_minutes: int
    max_otp_attempts: int
    access_token_lifetime: int
    refresh_token_lifetime: int


@dataclass(frozen=True)
class CorsConfig:
    """
    CORS configuration.
    """

    allow_credentials: bool
    allowed_origins: list
    trusted_origins: list
    internal_ips: list
    allowed_hosts: list


class Config:
    """
    Main application configuration class.
    """

    def __init__(self) -> None:
        """
        Initialize all application settings.
        """

        self.app = AppConfig(
            stage=self._get_required("STAGE"),
            debug=self._get_bool("DEBUG"),
            secret_key=self._get_required("SECRET_KEY"),
            base_url=self._get_required("BASE_URL"),
            admin_url=self._get_required("ADMIN_URL"),
        )

        self.i18n = InternationalizationConfig(
            language_code=self._get_required("LANGUAGE_CODE"),
            time_zone=self._get_required("TIME_ZONE"),
            use_i18n=self._get_bool("USE_I18N"),
            use_tz=self._get_bool("USE_TZ"),
        )

        self.email = EmailConfig(
            backend=self._get_required("EMAIL_BACKEND"),
            host=self._get_required("EMAIL_HOST"),
            port=self._get_int("EMAIL_PORT"),
            use_tls=self._get_bool("EMAIL_USE_TLS"),
            use_ssl=self._get_bool("EMAIL_USE_SSL"),
            host_user=self._get_required("EMAIL_HOST_USER"),
            host_password=self._get_required("EMAIL_HOST_PASSWORD"),
            default_from_email=self._get_required("DEFAULT_FROM_EMAIL"),
            max_retry_attempts=self._get_int("MAX_RETRY_ATTEMPTS"),
        )

        self.celery = CeleryConfig(
            broker_url=self._get_required("CELERY_BROKER_URL"),
            result_backend=self._get_required("CELERY_RESULT_BACKEND"),
        )

        self.auth = AuthConfig(
            otp_length=self._get_int("OTP_LENGTH"),
            otp_ttl_minutes=self._get_int("OTP_TTL_MINUTES"),
            max_otp_attempts=self._get_int("MAX_OTP_ATTEMPTS"),
            access_token_lifetime=self._get_int("ACCESS_TOKEN_LIFETIME"),
            refresh_token_lifetime=self._get_int("REFRESH_TOKEN_LIFETIME"),
        )

        self.cors = CorsConfig(
            allow_credentials=self._get_bool("CORS_ALLOW_CREDENTIALS"),
            allowed_origins=self._get_list("CORS_ALLOWED_ORIGINS"),
            trusted_origins=self._get_list("CSRF_TRUSTED_ORIGINS"),
            internal_ips=self._get_list("INTERNAL_IPS"),
            allowed_hosts=self._get_list("ALLOWED_HOSTS"),
        )

    @staticmethod
    def _get_required(key: str) -> str:
        """
        Get required environment variable.

        Args:
            key: Environment variable name.

        Returns:
            str: Environment variable value.

        Raises:
            ValueError: If variable is missing.
        """

        value = os.getenv(key)

        if not value:
            raise ValueError(f"{key} is missing in .env")

        return value

    @staticmethod
    def _get_list(key: str) -> list:
        """
        Get list environment variable.

        Args:
            key: Environment variable name.

        Returns:
            list: Parsed list value.
        """

        value = Config._get_required(key)

        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def _get_bool(key: str) -> bool:
        """
        Get boolean environment variable.

        Args:
            key: Environment variable name.

        Returns:
            bool: Parsed boolean value.
        """

        return os.getenv(key, "False").strip().lower() in (
            "true",
            "1",
            "yes",
            "on",
        )

    @staticmethod
    def _get_int(key: str) -> int:
        """
        Get integer environment variable.

        Args:
            key: Environment variable name.

        Returns:
            int: Parsed integer value.
        """

        value = Config._get_required(key)

        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{key} must be an integer") from exc


# Global configuration instance
config = Config()
