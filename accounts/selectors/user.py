from typing import Optional
from accounts.models import UserModel
from accounts.enums import UserRole, UserStatus


class UserSelector:
    """
    Read-only user state checks.
    No DB writes. No side effects.
    """

    @staticmethod
    def is_active(user: Optional[UserModel]) -> bool:
        """Check if user is active."""
        return bool(user and user.status == UserStatus.ACTIVE)

    @staticmethod
    def is_admin(user: Optional[UserModel]) -> bool:
        """Check admin privileges."""
        return bool(user and user.role == UserRole.ADMIN and user.is_staff)

    @staticmethod
    def is_superuser(user: Optional[UserModel]) -> bool:
        """Check superuser privileges."""
        return bool(
            user
            and user.role == UserRole.SUPERUSER
            and user.is_superuser
            and user.is_staff
        )
