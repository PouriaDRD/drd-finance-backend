import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from .category import CategoryModel
from finance.enums import TransactionType

User = get_user_model()


class TransactionModel(models.Model):
    """
    Financial transaction model
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    description = models.TextField(blank=True, null=True)

    amount = models.BigIntegerField(default=0)

    type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.INCOME,
    )

    date = models.DateField(
        auto_now_add=False,
        default=timezone.now,
    )

    month = models.PositiveIntegerField(default=1)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
        ]

    def __str__(self):
        return f"{self.amount} ({self.date}) {self.month}"

    @property
    def is_expense(self):
        return self.type == TransactionType.EXPENSE

    @property
    def is_income(self):
        return self.type == TransactionType.INCOME
