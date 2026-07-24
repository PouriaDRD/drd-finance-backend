import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from config.utils import APIResponse
from accounts.api.serializers import UserSerializer

logger = logging.getLogger("accounts.user")


class UserAPIView(RetrieveAPIView):
    """
    Retrieve authenticated user.
    """

    http_method_names = ["get"]

    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get(self, request: Request, *args, **kwargs):
        try:
            user = request.user

            serializer = self.serializer_class(user)

            logger.info(f"User data retrieved for user: {user}")

            return APIResponse.success(
                data=serializer.data,
                message="اطلاعات کاربر با موفقیت دریافت شد.",
            )

        except Exception as e:
            logger.error(f"Error retrieving user data: {e}")
            return APIResponse.error(
                message=f"خطا در دریافت اطلاعات کاربر",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
