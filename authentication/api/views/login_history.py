import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from config.utils import APIResponse
from authentication.models import LoginHistoryModel
from authentication.api.serializers import LoginHistorySerializer

logger = logging.getLogger("authentication.login-history")


class MyLoginHistoryAPIView(ListAPIView):
    """
    API endpoint for user login history.
    """

    http_method_names = ["get"]

    permission_classes = [IsAuthenticated]
    serializer_class = LoginHistorySerializer

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):  # type: ignore

        return LoginHistoryModel.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get(self, request: Request, *args, **kwargs):
        try:
            user = request.user
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            logger.info(f"User login history retrieved: {str(user)}")
            return APIResponse.success(
                data=serializer.data,
                message="داده های ورود شما با موفقیت دریافت شد.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error getting user login history: {e}")
            return APIResponse.error(
                message="خطا در دریافت ورود شما رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
