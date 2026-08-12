from datetime import datetime

from django.db.models import QuerySet

from .csv import create_csv_response
from .excel import create_excel_response
from finance.models import TransactionModel


def _transaction_rows(queryset: QuerySet[TransactionModel]):
    """
    Convert transactions into export rows.
    """

    for transaction in queryset:
        category = transaction.category

        yield [
            str(transaction.id),
            transaction.user.email if transaction.user else "",
            category.name if category else "بدون دسته‌بندی",
            category.get_type_display if category else "",
            transaction.get_type_display,
            transaction.amount,
            transaction.absolute_amount,
            transaction.description or "",
            transaction.get_persian_date(),
            transaction.get_persian_month_name(),
            transaction.year,
            transaction.month,
            transaction.date.strftime("%Y-%m-%d") if transaction.date else "",
            (
                transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if transaction.created_at
                else ""
            ),
        ]


TRANSACTION_HEADERS = [
    "شناسه",
    "ایمیل کاربر",
    "دسته‌بندی",
    "نوع دسته‌بندی",
    "نوع تراکنش",
    "مبلغ",
    "مبلغ مطلق",
    "توضیحات",
    "تاریخ شمسی",
    "ماه شمسی",
    "سال شمسی",
    "شماره ماه",
    "تاریخ میلادی",
    "تاریخ ایجاد",
]


def export_transactions_csv(queryset: QuerySet):
    """
    Export transactions as CSV.
    """

    filename = f"transactions_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return create_csv_response(
        filename=filename,
        headers=TRANSACTION_HEADERS,
        rows=_transaction_rows(queryset),
    )


def export_transactions_excel(queryset: QuerySet):
    """
    Export transactions as Excel.
    """

    filename = f"transactions_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return create_excel_response(
        filename=filename,
        sheet_name="Transactions",
        headers=TRANSACTION_HEADERS,
        rows=_transaction_rows(queryset),
        number_columns={
            5,  # amount
            6,  # absolute amount
            10,  # year
            11,  # month
        },
    )
