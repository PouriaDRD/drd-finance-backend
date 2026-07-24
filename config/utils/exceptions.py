import logging

from rest_framework import status
from rest_framework.views import exception_handler

from config.utils import APIResponse

logger = logging.getLogger("errors")


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    """

    response = exception_handler(exc, context)

    if response is not None:
        logger.warning(
            "API validation error: %s",
            str(exc),
        )

        return APIResponse.error(
            errors=response.data,
            message="درخواست ناموفق بود.",
            status_code=response.status_code,
        )

    logger.exception(
        "Unhandled exception",
        exc_info=exc,
    )

    return APIResponse.error(
        errors="Internal server error.",
        message="خطای غیرمنتظره رخ داد.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
