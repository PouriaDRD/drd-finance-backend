import logging

import jdatetime

from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.throttling import (
    ScopedRateThrottle,
)
from rest_framework.views import APIView

from config.utils import APIResponse

from finance.exports import (
    export_transactions_csv,
    export_transactions_excel,
)
from finance.repositories import (
    TransactionRepository,
)

logger = logging.getLogger(
    "finance.transaction.export",
)


class CurrentMonthTransactionsExportAPIView(APIView):
    """
    Export authenticated user's transactions
    for the current Persian month.

    Supported formats:
    - csv
    - xlsx
    """

    http_method_names = [
        "get",
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    throttle_scope = "user"

    throttle_classes = [
        ScopedRateThrottle,
    ]

    def get(
        self,
        request: Request,
        file_type: str,
        *args,
        **kwargs,
    ):
        try:
            normalized_file_type = file_type.strip().lower()

            if normalized_file_type not in {
                "csv",
                "xlsx",
            }:
                return APIResponse.error(
                    message=(
                        "فرمت خروجی نامعتبر است. " "فرمت‌های مجاز CSV و Excel هستند."
                    ),
                    status_code=(status.HTTP_400_BAD_REQUEST),
                )

            # =============================================
            # Current Jalali period
            # =============================================

            now = timezone.now()

            local_now = timezone.localtime(now) if timezone.is_aware(now) else now

            persian_date = jdatetime.date.fromgregorian(
                date=local_now.date(),
            )

            current_year = persian_date.year

            current_month = persian_date.month

            # =============================================
            # User transactions
            # =============================================

            queryset = TransactionRepository.get_by_persian_month(
                user_id=request.user.id,
                year=current_year,
                month=current_month,
            ).select_related(
                "user",
                "category",
            )

            filename_prefix = (
                "transactions_current_month_" f"{current_year}_" f"{current_month:02d}"
            )

            # =============================================
            # Export
            # =============================================

            if normalized_file_type == "csv":
                response = export_transactions_csv(
                    queryset,
                    filename_prefix=(filename_prefix),
                )

            else:
                response = export_transactions_excel(
                    queryset,
                    filename_prefix=(filename_prefix),
                )

            logger.info(
                (
                    "User %s exported current "
                    "Persian month transactions "
                    "for %s/%s as %s"
                ),
                request.user,
                current_year,
                current_month,
                normalized_file_type,
            )

            return response

        except Exception as exc:
            logger.exception(
                ("Current month transaction " "export failed for user %s: %s"),
                request.user,
                exc,
            )

            return APIResponse.error(
                message=("خطا در ایجاد خروجی " "تراکنش‌های ماه جاری رخ داد."),
                status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR),
            )
