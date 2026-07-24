import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from config.utils import APIResponse
from authentication.api.serializers import RegisterSerializer

logger = logging.getLogger("authentication.register")


class RegisterAPIView(CreateAPIView):
    """
    Register a new user.
    """

    http_method_names = ["post"]

    serializer_class = RegisterSerializer

    permission_classes = [AllowAny]

    throttle_scope = "register"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        try:
            serializer = self.get_serializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)

            result = serializer.save()

            logger.info(f"User Registered successfully: {result['user']}")

            return APIResponse.success(
                data=result,
                message="حساب کاربری با موفقیت ایجاد شد.",
                status_code=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            logger.warning(f"Error registering user: {e.get_codes()}")
            if "user_already_exists" in e.get_codes():  # type: ignore
                return APIResponse.error(
                    message=f"حساب کاربری قبلا ایجاد شده است.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            # {'referral_code': [ErrorDetail(string='کد دعوت نامعتبر است.', code='invalid_code')]}
            if "invalid_code" in e.get_codes() or "referral_code" in e.detail:  # type: ignore
                return APIResponse.error(
                    message=f"کد دعوت نامعتبر است.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            return APIResponse.error(
                message=f"خطا در ایجاد حساب کاربری",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return APIResponse.error(
                message=f"خطا در ایجاد حساب کاربری",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
