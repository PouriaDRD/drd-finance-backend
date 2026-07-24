from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    BANNED = "banned", "Banned"
    INACTIVE = "inactive", "Inactive"
