import logging
from urllib.parse import quote

import jdatetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from config.utils import APIResponse

from finance.exports import (
    export_transactions_csv,
    export_transactions_excel,
)
from finance.models import TransactionModel
from finance.repositories import TransactionRepository


logger = logging.getLogger(
    "finance.transaction.export",
)


class PersianMonthTransactionsExportAPIView(APIView):
    """
    Export the authenticated user's transactions for a selected
    Persian (Solar Hijri) year and month.

    Supported formats:
    - csv
    - xlsx
    """

    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get(
        self,
        request: Request,
        year: int,
        month: int,
        file_type: str,
        *args,
        **kwargs,
    ):
        try:
            normalized_file_type = file_type.strip().lower()

            validation_error = self._validate_period(
                year=year,
                month=month,
            )

            if validation_error:
                return APIResponse.error(
                    message=validation_error,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if normalized_file_type not in {"csv", "xlsx"}:
                return APIResponse.error(
                    message=(
                        "فرمت خروجی نامعتبر است. "
                        "فرمت‌های مجاز CSV و Excel هستند."
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            queryset = (
                TransactionRepository.get_by_persian_month(
                    user_id=request.user.id,
                    year=year,
                    month=month,
                )
                .select_related("user", "category")
                .order_by("-date", "-created_at")
            )

            month_name = TransactionModel(
                year=year,
                month=month,
            ).get_persian_month_name()

            filename = (
                f"{month_name} {year}."
                f"{normalized_file_type}"
            )

            if normalized_file_type == "csv":
                response = export_transactions_csv(queryset)
            else:
                response = export_transactions_excel(queryset)

            # RFC 5987 / UTF-8 filename support for Persian file names.
            response["Content-Disposition"] = (
                "attachment; filename*=UTF-8''"
                f"{quote(filename)}"
            )

            logger.info(
                (
                    "User %s exported Persian month transactions "
                    "for %s/%s as %s"
                ),
                request.user,
                year,
                month,
                normalized_file_type,
            )

            return response

        except Exception as exc:
            logger.exception(
                (
                    "Persian month transaction export failed "
                    "for user %s, period %s/%s: %s"
                ),
                request.user,
                year,
                month,
                exc,
            )

            return APIResponse.error(
                message=(
                    "خطا در ایجاد خروجی تراکنش‌های "
                    "دوره انتخاب‌شده رخ داد."
                ),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def _validate_period(
        *,
        year: int,
        month: int,
    ) -> str | None:
        """Validate the requested Persian reporting period."""

        if not 1 <= month <= 12:
            return "ماه باید بین ۱ تا ۱۲ باشد."

        current_date = jdatetime.date.today()

        if year < 1400 or year > current_date.year:
            return "سال انتخاب‌شده خارج از بازه مجاز است."

        if (
            year == current_date.year
            and month > current_date.month
        ):
            return "امکان دریافت خروجی برای ماه‌های آینده وجود ندارد."

        return None
