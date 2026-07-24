from typing import Optional
from django.contrib.auth.models import BaseUserManager
from accounts.enums import UserRole, UserStatus


class UserManager(BaseUserManager):
    """Custom manager for the UserModel, handling user and superuser creation."""

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
        """Create a new user with the given email and password."""

        if not email:
            raise ValueError("ایمیل مورد نظر وارد نشده است.")

        # Normalize email
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            email_verified=False,
            is_superuser=False,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # for OAuth cases

        user.save(using=self._db)

        return user

    def create_superuser(
        self, email: str, password: Optional[str] = None, **extra_fields
    ):
        """Create a new superuser with the given email and password."""
        user = self.create_user(email=email, password=password, **extra_fields)

        # Set the user role to admin and status to active
        user.is_superuser = True
        user.role = UserRole.SUPERUSER
        user.status = UserStatus.ACTIVE

        user.save(using=self._db)

        return user
