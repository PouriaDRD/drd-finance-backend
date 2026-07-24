import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)

from config.utils import APIResponse

from finance.services import TransactionService
from finance.repositories import TransactionRepository
from finance.api.serializers import (
    TransactionSerializer,
    PersianMonthSummarySerializer,
    YearlySummarySerializer,
    TransactionCreateSerializer,
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


class TransactionCreateAPIView(CreateAPIView):
    """
    Create new transaction.
    """

    http_method_names = ["post"]

    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    serializer_class = TransactionCreateSerializer

    def post(self, request: Request, *args, **kwargs):
        """
        Create a new transaction.
        """

        try:
            # ========== Serializer ==========
            serializer = self.get_serializer_class()(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            # ========== Service ==========
            transaction = TransactionService.create_transaction(
                user=request.user,
                **serializer.validated_data,  # type: ignore
            )

            # ========== Response ==========
            response_serializer = TransactionSerializer(transaction)

            logger.info(
                f"Transaction created successfully: {transaction.id}, "
                f"user: {request.user}"
            )

            return APIResponse.success(
                data=response_serializer.data,
                message="تراکنش با موفقیت ایجاد شد.",
                status_code=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            logger.warning(f"Error creating transaction: {e.detail}")
            return APIResponse.error(
                message="خطا در ایجاد تراکنش رخ داد.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception(f"Transaction creation failed: {e}")
            return APIResponse.error(
                message="خطا در ایجاد تراکنش رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransactionUpdateAPIView(UpdateAPIView):
    """
    Update existing transaction.
    """

    http_method_names = ["patch"]

    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    serializer_class = TransactionCreateAPIView

    def patch(self, request: Request, *args, **kwargs):
        """
        Update a transaction.
        """

        try:
            # ========== Get transaction ID ==========
            transaction_id = kwargs.get("transaction_id")

            if not transaction_id:
                return APIResponse.error(
                    message="شناسه تراکنش الزامی است.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # ========== Serializer ==========
            serializer = self.get_serializer_class()(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            # ========== Service ==========
            transaction = TransactionService.update_transaction(
                user=request.user,
                transaction_id=transaction_id,
                **serializer.validated_data,
            )

            # ========== Response ==========
            response_serializer = TransactionSerializer(transaction)

            logger.info(
                f"Transaction updated successfully: {transaction.id}, "
                f"user: {request.user}"
            )

            return APIResponse.success(
                data=response_serializer.data,
                message="تراکنش با موفقیت به‌روزرسانی شد.",
                status_code=status.HTTP_200_OK,
            )

        except ValidationError as e:
            logger.warning(f"Error updating transaction: {e.detail}")
            return APIResponse.error(
                message="خطا در به‌روزرسانی تراکنش رخ داد.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception(f"Transaction update failed: {e}")
            return APIResponse.error(
                message="خطا در به‌روزرسانی تراکنش رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransactionDeleteAPIView(DestroyAPIView):
    """
    Delete transaction.
    """

    http_method_names = ["delete"]

    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def delete(self, request: Request, *args, **kwargs):
        """
        Delete a transaction.
        """

        try:
            # ========== Get transaction ID ==========
            transaction_id = kwargs.get("transaction_id")

            if not transaction_id:
                return APIResponse.error(
                    message="شناسه تراکنش الزامی است.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # ========== Service ==========
            TransactionService.delete_transaction(
                user=request.user,
                transaction_id=transaction_id,
            )

            logger.info(
                f"Transaction deleted successfully: {transaction_id}, "
                f"user: {request.user}"
            )

            return APIResponse.success(
                message="تراکنش با موفقیت حذف شد.",
                status_code=status.HTTP_200_OK,
            )

        except ValidationError as e:
            logger.warning(f"Error deleting transaction: {e.detail}")
            return APIResponse.error(
                message="خطا در حذف تراکنش رخ داد.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception(f"Transaction delete failed: {e}")
            return APIResponse.error(
                message="خطا در حذف تراکنش رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
