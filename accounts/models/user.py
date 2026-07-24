import uuid
from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .user_manager import UserManager
from accounts.enums import UserRole, UserStatus


class UserModel(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that replaces Django's default user model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Email is required for user creation and must be unique
    email = models.EmailField(
        unique=True,
        validators=[
            EmailValidator(
                message="ایمل وارد شده معتبر نیست.",
                code="invalid_email",
            )
        ],
        help_text="یک ایمیل معتبر وارد کنید.",
    )
    email_verified = models.BooleanField(default=False)
    # User full name
    name = models.CharField(max_length=255, blank=True, null=True)

    # Status for the user (active, banned, deleted)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True,
    )
    # Role for the user (admin, user, menu owner)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
    )

    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )

    # Timestamps for user creation and last update
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Attach the custom manager
    objects = UserManager()

    # Set the USERNAME_FIELD to 'email' for login
    USERNAME_FIELD = "email"

    @property
    def is_staff(self) -> bool:
        """Check if the user is staff."""
        result: bool = (
            self.is_superuser
            or self.role == UserRole.ADMIN
            or self.role == UserRole.SUPERUSER
        )
        return result

    @property
    def is_active(self) -> bool:  # type: ignore
        """Check if the user is active."""
        return self.status == UserStatus.ACTIVE

    def __str__(self) -> str:
        """String representation of the user."""
        return self.email

    class Meta:
        """Meta class for the UserModel."""

        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)
