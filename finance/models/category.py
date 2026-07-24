import uuid
from django.db import models
from django.contrib.auth import get_user_model

from finance.enums import CategoryType

User = get_user_model()


class CategoryModel(models.Model):
    """
    Category model for income/expense classification
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    name = models.CharField(
        max_length=256,
        help_text="Category name (e.g., Food, Salary, Rent)",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Category description",
    )

    type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
        default=CategoryType.INCOME,
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="FontAwesome or emoji icon",
    )

    color = models.CharField(
        max_length=7,
        default="#6C757D",
        help_text="Hex color code (e.g., #FF6B6B)",
    )

    is_archived = models.BooleanField(
        default=True,
        help_text="Archived categories won't appear in dropdowns",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["type", "name"]

        verbose_name = "Category"
        verbose_name_plural = "Categories"
        # each user can have a unique combination of name and type
        unique_together = [["user", "name", "type"]]

    def __str__(self):
        return f"{self.name} {self.type}"

    @property
    def is_expense(self):
        return self.type == CategoryType.EXPENSE

    @property
    def is_income(self):
        return self.type == CategoryType.INCOME
