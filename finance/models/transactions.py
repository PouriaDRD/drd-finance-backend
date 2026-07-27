import uuid
import jdatetime
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .category import CategoryModel
from finance.enums import TransactionType, CategoryType

User = get_user_model()

CURRENT_MONTH = jdatetime.date.today().month
CURRENT_YEAR = jdatetime.date.today().year

MIN_YEAR = 1400
MAX_YEAR = CURRENT_YEAR


class TransactionModel(models.Model):
    """
    Financial transaction model
    IMPORTANT: amount is stored as:
    - Positive (+) for INCOME
    - Negative (-) for EXPENSE
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

    amount = models.BigIntegerField(
        default=0,
        help_text="Positive for income, Negative for expense",
    )

    type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.INCOME,
    )

    date = models.DateField(
        auto_now_add=False,
        default=timezone.now,
    )

    month = models.PositiveIntegerField(
        default=1,
        help_text="Persian month (1: Farvardin, ..., 12: Esfand)",
    )

    year = models.PositiveIntegerField(
        default=1405,
        help_text="Persian year (Solar Hijri)",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
            models.Index(fields=["user", "type"]),
            models.Index(fields=["user", "year", "month"]),
        ]

    def __str__(self):
        sign = "+" if self.is_income else "-"
        return f"{sign}{abs(self.amount):,} - {self.date}"

    @property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.type == TransactionType.EXPENSE or self.amount < 0

    @property
    def is_income(self):
        """Check if transaction is income"""
        return self.type == TransactionType.INCOME or self.amount > 0

    @property
    def absolute_amount(self):
        """Return absolute value of amount (always positive)"""
        return abs(self.amount)

    @property
    def signed_amount(self):
        """Return amount with sign (already stored with sign)"""
        return self.amount

    def get_display_amount(self):
        """Return formatted amount with sign for display"""
        sign = "+" if self.is_income else "-"
        return f"{sign}{self.absolute_amount:,}"

    def clean(self):
        """Validate amount and date"""
        if self.amount == 0:
            raise ValidationError({"amount": "Amount cannot be zero."})

        if not 1 <= self.month <= 12:
            raise ValidationError({"month": "Month must be between 1 and 12."})

        if self.month > CURRENT_MONTH:
            raise ValidationError(
                {"month": f"Month can not be greater than {CURRENT_MONTH}."}
            )

        if self.year < MIN_YEAR or self.year > MAX_YEAR:
            raise ValidationError(
                {"year": f"Year must be between {MIN_YEAR} and {MAX_YEAR}."}
            )

    def save(self, *args, **kwargs):
        """Auto-set month and validate before saving"""
        if self.date:
            persian = jdatetime.date.fromgregorian(date=self.date)
            self.month = persian.month
            self.year = persian.year

        if self.category and self.category.type:
            self.type = (
                TransactionType.INCOME
                if self.category.type == CategoryType.INCOME
                else TransactionType.EXPENSE
            )

        if self.type == TransactionType.INCOME:
            if self.amount < 0:
                self.amount = abs(self.amount)

        elif self.type == TransactionType.EXPENSE:
            if self.amount > 0:
                self.amount = -abs(self.amount)

        self.full_clean()

        super().save(*args, **kwargs)

    def get_persian_date(self):
        """Convert Gregorian date to Persian (Solar Hijri)"""
        if self.date:
            persian = jdatetime.date.fromgregorian(date=self.date)
            return persian.strftime("%Y/%m/%d")
        return ""

    def get_persian_month_name(self):
        """Get Persian month name"""
        persian_months = {
            1: "فروردین",
            2: "اردیبهشت",
            3: "خرداد",
            4: "تیر",
            5: "مرداد",
            6: "شهریور",
            7: "مهر",
            8: "آبان",
            9: "آذر",
            10: "دی",
            11: "بهمن",
            12: "اسفند",
        }
        return persian_months.get(self.month, str(self.month))

    def get_persian_date_display(self):
        """Get full Persian date display"""
        if self.date:
            persian = jdatetime.date.fromgregorian(date=self.date)
            return f"{persian.day} {self.get_persian_month_name()} {persian.year}"
        return ""

    @classmethod
    def filter_by_persian_month(cls, user, year, month):
        """Filter transactions by Persian year and month"""
        return cls.objects.filter(user=user, year=year, month=month)

    @classmethod
    def get_monthly_summary(cls, user, year, month):
        """Get income, expense and balance for a specific Persian month"""
        qs = cls.filter_by_persian_month(user, year, month)

        income = (
            qs.filter(type=TransactionType.INCOME).aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )

        expense = (
            qs.filter(type=TransactionType.EXPENSE).aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )

        return {
            "income": income,
            "expense": abs(expense),
            "balance": income + expense,  # expense منفی هست
            "count": qs.count(),
        }

    @classmethod
    def get_total_income(cls, user=None):
        """Get total income for a user"""
        qs = cls.objects.filter(type=TransactionType.INCOME)
        if user:
            qs = qs.filter(user=user)
        return qs.aggregate(total=models.Sum("amount"))["total"] or 0

    @classmethod
    def get_total_expense(cls, user=None):
        """Get total expense for a user (returns positive value)"""
        qs = cls.objects.filter(type=TransactionType.EXPENSE)
        if user:
            qs = qs.filter(user=user)
        total = qs.aggregate(total=models.Sum("amount"))["total"] or 0
        return abs(total)

    @classmethod
    def get_balance(cls, user=None):
        """Get net balance (income - expense)"""
        qs = cls.objects.all()
        if user:
            qs = qs.filter(user=user)
        total = qs.aggregate(total=models.Sum("amount"))["total"] or 0
        return total
