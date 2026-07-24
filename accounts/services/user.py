from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import UserModel
from accounts.repositories import UserRepository


class UserService:

    @classmethod
    @transaction.atomic
    def create_user(cls, email: str, password: str, **extra_fields):

        email = email.strip().lower()

        if UserRepository.get_by_email(email):
            raise ValidationError(
                "حساب کاربری قبلا ایجاد شده است.", code="user_already_exists"
            )

        new_user = UserRepository.create(
            email=email,
            password=password,
            **extra_fields,
        )

        return new_user

    @classmethod
    @transaction.atomic
    def verify_email(cls, user: UserModel):

        user.email_verified = True

        return UserRepository.save(
            user,
            update_fields=["email_verified"],
        )

    @classmethod
    @transaction.atomic
    def change_password(cls, user: UserModel, password: str):

        user.set_password(password)

        return UserRepository.save(
            user,
            update_fields=["password"],
        )

    @classmethod
    @transaction.atomic
    def update_last_login(cls, user: UserModel):

        user.last_login = timezone.now()

        UserRepository.save(
            user,
            update_fields=["last_login"],
        )
