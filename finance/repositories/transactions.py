import jdatetime
from datetime import date
from typing import Optional, cast
from django.utils import timezone
from django.db.models import Sum, Q, Count

from finance.enums import TransactionType, CategoryType
from finance.models import TransactionModel, CategoryModel


class TransactionRepository:
    """
    Only database operations.
    """

    @staticmethod
    def create(**kwargs):
        """
        Create a new transaction.
        If date is provided, month and year will be auto-set from Persian date.
        """
        return TransactionModel.objects.create(**kwargs)

    @staticmethod
    def update(transaction: TransactionModel, **kwargs):
        """
        Update a transaction with given fields.
        If date is updated, month and year will be auto-set from Persian date.
        """
        for key, value in kwargs.items():
            setattr(transaction, key, value)

        if "date" in kwargs:
            persian = jdatetime.date.fromgregorian(date=transaction.date)
            transaction.month = persian.month
            transaction.year = persian.year

        update_fields = list(kwargs.keys())
        if "date" in kwargs:
            update_fields.extend(["month", "year"])

        category = cast(Optional[CategoryModel], kwargs.get("category", None))

        if category:
            transaction.type = (
                TransactionType.INCOME
                if category.type == CategoryType.INCOME
                else TransactionType.EXPENSE
            )
            update_fields.extend(["type"])

        transaction.save(update_fields=update_fields)

        return transaction

    @staticmethod
    def get_user_transaction(user_id, transaction_id):
        """Get a single transaction by ID for a specific user"""
        return TransactionModel.objects.select_related(
            "user",
            "category",
        ).get(
            id=transaction_id,
            user_id=user_id,
        )

    @staticmethod
    def get_user_transactions(user_id):
        """Get all transactions for a user"""
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
            )
            .select_related(
                "user",
                "category",
            )
            .order_by(
                "-date",
                "-created_at",
            )
        )

    @staticmethod
    def get_by_persian_month(user_id, year: int, month: int):
        """
        Get transactions by Persian (Solar Hijri) year and month.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                year=year,
                month=month,
            )
            .select_related(
                "category",
            )
            .order_by(
                "-date",
            )
        )

    @staticmethod
    def get_by_persian_year(user_id, year: int):
        """
        Get transactions by Persian (Solar Hijri) year.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                year=year,
            )
            .select_related(
                "category",
            )
            .order_by(
                "-date",
            )
        )

    @staticmethod
    def get_by_persian_date_range(
        user_id, start_year: int, start_month: int, end_year: int, end_month: int
    ):
        """
        Get transactions by Persian date range.
        """
        filter_condition = Q()

        if start_year == end_year:
            filter_condition = Q(
                year=start_year,
                month__gte=start_month,
                month__lte=end_month,
            )
        else:
            filter_condition |= Q(
                year=start_year,
                month__gte=start_month,
            )
            filter_condition |= Q(
                year__gt=start_year,
                year__lt=end_year,
            )
            filter_condition |= Q(
                year=end_year,
                month__lte=end_month,
            )

        return (
            TransactionModel.objects.filter(
                user_id=user_id,
            )
            .filter(filter_condition)
            .select_related("category")
            .order_by("-year", "-month", "-date")
        )

    @staticmethod
    def get_by_month(user_id, month: int):
        """
        Get transactions by Gregorian month.
        DEPRECATED: Use get_by_persian_month instead.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                month=month,
            )
            .select_related(
                "category",
            )
            .order_by(
                "-date",
            )
        )

    @staticmethod
    def get_by_date_range(user_id, start_date: date, end_date: date):
        """
        Get transactions by Gregorian date range.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                date__range=(
                    start_date,
                    end_date,
                ),
            )
            .select_related(
                "category",
            )
            .order_by(
                "-date",
            )
        )

    @staticmethod
    def get_by_type(user_id, transaction_type):
        """
        Get transactions by type (INCOME/EXPENSE).
        """
        return TransactionModel.objects.filter(
            user_id=user_id,
            type=transaction_type,
        ).select_related(
            "category",
        )

    @staticmethod
    def get_total_amount(user_id):
        """
        Get total amount of all transactions (including negative).
        This equals net balance.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

    @staticmethod
    def get_total_income(user_id):
        """
        Get total income (positive amount).
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                type=TransactionType.INCOME,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

    @staticmethod
    def get_total_expense(user_id):
        """
        Get total expense (positive value).
        """
        total = (
            TransactionModel.objects.filter(
                user_id=user_id,
                type=TransactionType.EXPENSE,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return abs(total)

    @staticmethod
    def get_balance(user_id):
        """
        Get net balance (income - expense).
        """
        income = TransactionRepository.get_total_income(user_id)
        expense = TransactionRepository.get_total_expense(user_id)
        return income - expense

    @staticmethod
    def get_persian_month_income(user_id, year: int, month: int):
        """
        Get income for a specific Persian month.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                year=year,
                month=month,
                type=TransactionType.INCOME,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

    @staticmethod
    def get_persian_month_expense(user_id, year: int, month: int):
        """
        Get expense for a specific Persian month (positive value).
        """
        total = (
            TransactionModel.objects.filter(
                user_id=user_id,
                year=year,
                month=month,
                type=TransactionType.EXPENSE,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return abs(total)

    @staticmethod
    def get_persian_month_balance(user_id, year: int, month: int):
        """
        Get net balance for a specific Persian month.
        """
        income = TransactionRepository.get_persian_month_income(user_id, year, month)
        expense = TransactionRepository.get_persian_month_expense(user_id, year, month)
        return income - expense

    @staticmethod
    def get_persian_month_summary(user_id, year: int, month: int):
        """
        Get full summary for a Persian month.
        """
        transactions = TransactionRepository.get_by_persian_month(user_id, year, month)

        income = (
            transactions.filter(type=TransactionType.INCOME).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        expense = (
            transactions.filter(type=TransactionType.EXPENSE).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        return {
            "year": year,
            "month": month,
            "month_name": TransactionModel(
                year=year, month=month
            ).get_persian_month_name(),
            "income": income,
            "expense": abs(expense),
            "balance": income + expense,
            "count": transactions.count(),
            "transactions": transactions,
        }

    @staticmethod
    def get_month_income(user_id, month: int):
        """
        Get income for a specific Gregorian month.
        DEPRECATED: Use get_persian_month_income instead.
        """
        return (
            TransactionModel.objects.filter(
                user_id=user_id,
                month=month,
                type=TransactionType.INCOME,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

    @staticmethod
    def get_month_expense(user_id, month: int):
        """
        Get expense for a specific Gregorian month (positive value).
        DEPRECATED: Use get_persian_month_expense instead.
        """
        total = (
            TransactionModel.objects.filter(
                user_id=user_id,
                month=month,
                type=TransactionType.EXPENSE,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return abs(total)

    @staticmethod
    def get_month_balance(user_id, month: int):
        """
        Get net balance for a specific Gregorian month.
        DEPRECATED: Use get_persian_month_balance instead.
        """
        income = TransactionRepository.get_month_income(user_id, month)
        expense = TransactionRepository.get_month_expense(user_id, month)
        return income - expense

    @staticmethod
    def get_yearly_report(
        user_id,
        year: int,
    ):
        """
        Get yearly report with monthly breakdown.
        """

        transactions = TransactionRepository.get_by_persian_year(
            user_id,
            year,
        )

        monthly_data = (
            transactions.values("month")
            .annotate(
                income=Sum(
                    "amount",
                    filter=Q(type=TransactionType.INCOME),
                ),
                expense=Sum(
                    "amount",
                    filter=Q(type=TransactionType.EXPENSE),
                ),
                count=Count("id"),
            )
            .order_by("month")
        )

        report = []

        monthly_map = {item["month"]: item for item in monthly_data}

        for month in range(1, 13):

            data = monthly_map.get(month, {})

            income = data.get("income") or 0

            expense = abs(data.get("expense") or 0)

            report.append(
                {
                    "month": month,
                    "month_name": (
                        TransactionModel(
                            month=month,
                            year=year,
                        ).get_persian_month_name()
                    ),
                    "income": income,
                    "expense": expense,
                    "balance": (income - expense),
                    "count": (data.get("count") or 0),
                }
            )

        total_income = sum(item["income"] for item in report)

        total_expense = sum(item["expense"] for item in report)

        return {
            "year": year,
            "monthly_report": report,
            "total_income": total_income,
            "total_expense": total_expense,
            "total_balance": (total_income - total_expense),
        }

    @staticmethod
    def get_category_summary(
        user_id, year: Optional[int] = None, month: Optional[int] = None
    ):
        """
        Get summary by category for a specific period.
        """
        queryset = TransactionModel.objects.filter(user_id=user_id)

        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)

        category_summary = (
            queryset.values("category__name", "category__type")
            .annotate(
                total_amount=Sum("amount"),
                count=Sum("id"),
                income=Sum("amount", filter=Q(type=TransactionType.INCOME)),
                expense=Sum("amount", filter=Q(type=TransactionType.EXPENSE)),
            )
            .order_by("-total_amount")
        )

        return category_summary

    @staticmethod
    def get_daily_summary(user_id, year: int, month: int):
        """
        Get daily summary for a specific Persian month.
        """
        transactions = TransactionRepository.get_by_persian_month(user_id, year, month)

        daily_summary = (
            transactions.values("date")
            .annotate(
                income=Sum("amount", filter=Q(type=TransactionType.INCOME)),
                expense=Sum("amount", filter=Q(type=TransactionType.EXPENSE)),
                count=Count("id"),
            )
            .order_by("date")
        )

        return daily_summary

    @staticmethod
    def get_dashboard_data(user_id):
        """
        Get all data needed for dashboard.
        """
        current_date = timezone.now().date()
        persian_current = jdatetime.date.fromgregorian(date=current_date)

        current_year = persian_current.year
        current_month = persian_current.month

        # all stats
        total_income = TransactionRepository.get_total_income(user_id)
        total_expense = TransactionRepository.get_total_expense(user_id)
        total_balance = total_income - total_expense

        # current month summary
        month_income = TransactionRepository.get_persian_month_income(
            user_id, current_year, current_month
        )
        month_expense = TransactionRepository.get_persian_month_expense(
            user_id, current_year, current_month
        )
        month_balance = month_income - month_expense

        recent_transactions = TransactionRepository.get_user_transactions(user_id)[:10]

        top_categories = TransactionRepository.get_category_summary(
            user_id, current_year, current_month
        )[:5]

        return {
            "total": {
                "income": total_income,
                "expense": total_expense,
                "balance": total_balance,
            },
            "current_month": {
                "year": current_year,
                "month": current_month,
                "month_name": TransactionModel(
                    year=current_year, month=current_month
                ).get_persian_month_name(),
                "income": month_income,
                "expense": month_expense,
                "balance": month_balance,
            },
            "recent_transactions": recent_transactions,
            "top_categories": top_categories,
        }
