import logging
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import update_last_login

from authentication.services import LoginHistoryService

UserModel = get_user_model()

logger = logging.getLogger("auth_backend")


class AuthBackend(BaseBackend):
    """
    Custom authentication backend allowing login by both email and username.
    """

    def authenticate(
        self, request: HttpRequest, username=None, password=None, **kwargs
    ):
        if not username or not password:
            return None
        user = None
        try:
            # try to find user by phone_number
            user = UserModel.objects.get(email__iexact=username)
        # except UserModel.DoesNotExist:
        #     # try to find user by username
        #     user = UserModel.objects.get(username__iexact=username)
        #     logger.info(f"User {username} failed login with invalid credentials")
        #     return None
        except UserModel.MultipleObjectsReturned:
            logger.error(
                f"Multiple users with same username or email found: {username}"
            )
            return None

        except UserModel.DoesNotExist:
            logger.info(f"User {username} failed login with invalid credentials")
            return None

        if user.check_password(password) and user.is_active:
            # update last login and send a security alert to user
            update_last_login(None, user)  # type: ignore
            logger.info(f"User {username} logged in successfully")
            self.alert_user(user, request)
            return user
        else:
            logger.info(f"User {username} failed login with invalid credentials")
            return None

    def get_user(self, user_id):
        return UserModel.objects.filter(pk=user_id).first()

    def alert_user(self, user, request):
        LoginHistoryService.create_success(
            user=user,  # type: ignore
            request=request,
        )
