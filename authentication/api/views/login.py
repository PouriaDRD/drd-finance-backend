import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from config.utils import APIResponse
from authentication.api.serializers import LoginSerializer

logger = logging.getLogger("authentication.login")


class LoginAPIView(GenericAPIView):
    """
    User login endpoint.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    throttle_scope = "login"
    throttle_classes = [ScopedRateThrottle]

    http_method_names = ["post"]

    def post(self, request: Request, *args, **kwargs):

        try:
            serializer = self.get_serializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)

            result = serializer.save()

            logger.info(f"User logged in successfully: {result['user']}")
            return APIResponse.success(
                data=result,
                message="ورود با موفقیت انجام شد.",
                status_code=status.HTTP_200_OK,
            )

        except ValidationError:
            return APIResponse.error(
                message="نام کاربری یا رمز عبور اشتباه است.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return APIResponse.error(
                message="نام کاربری یا رمز عبور اشتباه است.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
