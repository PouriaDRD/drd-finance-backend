from typing import Optional

from accounts.models import UserModel
from accounts.enums import UserRole


class UserRepository:
    """Only database operations."""

    @staticmethod
    def create(**kwargs) -> UserModel:
        return UserModel.objects.create_user(**kwargs)  # type: ignore

    @staticmethod
    def get_by_email(email: str) -> Optional[UserModel]:
        return UserModel.objects.filter(email=email).first()

    @staticmethod
    def get_admin_user() -> Optional[UserModel]:
        return UserModel.objects.filter(role=UserRole.SUPERUSER).first()

    @staticmethod
    def get_by_id(user_id: str) -> Optional[UserModel]:
        return UserModel.objects.filter(id=user_id).first()

    @staticmethod
    def save(user: UserModel, update_fields: list[str] | None = None):
        user.save(update_fields=update_fields)
        return user
