import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView

from config.utils import APIResponse

# from finance.services import TransactionService
from finance.repositories import TransactionRepository
from finance.api.serializers import (
    TransactionSerializer,
    PersianMonthSummarySerializer,
    YearlySummarySerializer,
)

logger = logging.getLogger("finance.transaction")


class MyTransactionsAPIView(ListAPIView):
    """
    API endpoint for user to get all of their transactions.
    """

    http_method_names = ["get"]

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):  # type: ignore
        qs = TransactionRepository.get_user_transactions(str(self.request.user.id))  # type: ignore
        return qs

    def get(self, request: Request, *args, **kwargs):
        try:
            user = request.user
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            logger.info(f"User requested transactions: {str(user)}")
            return APIResponse.success(
                data=serializer.data,
                message="داده های تراکنش با موفقیت دریافت شد.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error getting user login history: {e}")
            return APIResponse.error(
                message="خطا در دریافت تراکنش ها رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PersianMonthSummaryAPIView(ListAPIView):
    """
    Returns summary of a Persian month.
    """

    http_method_names = ["get"]

    permission_classes = (IsAuthenticated,)

    throttle_scope = "user"
    throttle_classes = (ScopedRateThrottle,)

    serializer_class = PersianMonthSummarySerializer

    def get(
        self,
        request: Request,
        year: int,
        month: int,
        *args,
        **kwargs,
    ):
        try:

            summary = TransactionRepository.get_persian_month_summary(
                user_id=request.user.id,
                year=year,
                month=month,
            )

            serializer = self.get_serializer(summary)

            logger.info(
                "User %s requested summary for %s/%s",
                request.user,
                year,
                month,
            )

            return APIResponse.success(
                data=serializer.data,
                message="خلاصه ماه با موفقیت دریافت شد.",
                status_code=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Error getting month summary.")

            return APIResponse.error(
                message="خطا در دریافت خلاصه ماه.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class YearlySummaryAPIView(ListAPIView):
    """
    Return yearly report with monthly breakdown.
    """

    http_method_names = ["get"]

    permission_classes = (IsAuthenticated,)

    throttle_scope = "user"
    throttle_classes = (ScopedRateThrottle,)

    serializer_class = YearlySummarySerializer

    def get(
        self,
        request: Request,
        year: int,
        *args,
        **kwargs,
    ):
        try:

            report = TransactionRepository.get_yearly_report(
                user_id=request.user.id,
                year=year,
            )

            serializer = self.get_serializer(report)

            logger.info(
                "User %s requested yearly report for %s",
                request.user,
                year,
            )

            return APIResponse.success(
                data=serializer.data,
                message="گزارش سالانه با موفقیت دریافت شد.",
                status_code=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Error getting yearly report.")

            return APIResponse.error(
                message="خطا در دریافت گزارش سالانه.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
