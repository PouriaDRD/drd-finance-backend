from rest_framework.request import Request
from django.contrib.auth import authenticate

from .token import TokenService
from .login_history import LoginHistoryService


from accounts.services import UserService
from authentication.exceptions import WrongEmailOrPasswordError


class AuthService:
    """
    Authentication business logic.
    """

    @classmethod
    def register(cls, email: str, password: str, name: str, request: Request):
        email = cls.normalize_email(email)

        user = UserService.create_user(
            email=email,
            password=password,
            name=name,
        )

        LoginHistoryService.create_success(
            user,
            request,
        )

        return cls.auth_response(user)

    @classmethod
    def login(cls, email: str, password: str, request: Request):
        email = cls.normalize_email(email)

        user = authenticate(
            request=request,  # type: ignore
            username=email,
            password=password,
        )

        if not user:
            raise WrongEmailOrPasswordError()

        return cls.auth_response(user)

    @classmethod
    def normalize_email(cls, email: str):
        return email.strip().lower()

    @classmethod
    def auth_response(cls, user):

        return {
            "user": str(user),
            **TokenService.generate(user),
        }
