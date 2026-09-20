import jdatetime

from django.db.models import QuerySet
from django.utils import timezone

from finance.models import TransactionModel

from .csv import create_csv_response
from .excel import create_excel_response

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


def _transaction_rows(
    queryset: QuerySet[TransactionModel],
):
    """
    Convert transactions into export rows.

    Both Persian and Gregorian dates are included in the
    exported file.
    """

    for transaction in queryset:
        category = transaction.category

        yield [
            str(transaction.id),
            (transaction.user.email if transaction.user else ""),
            (category.name if category else "بدون دسته‌بندی"),
            (category.get_type_display if category else ""),
            transaction.get_type_display,
            transaction.amount,
            transaction.absolute_amount,
            transaction.description or "",
            transaction.get_persian_date(),
            transaction.get_persian_month_name(),
            transaction.year,
            transaction.month,
            (
                transaction.date.strftime(
                    "%Y-%m-%d",
                )
                if transaction.date
                else ""
            ),
            (
                timezone.localtime(
                    transaction.created_at,
                ).strftime(
                    "%Y-%m-%d %H:%M:%S",
                )
                if transaction.created_at
                else ""
            ),
        ]


def _build_export_filename(
    *,
    extension: str,
    filename_prefix: str,
) -> str:
    """
    Build filename containing both Jalali and Gregorian dates.

    Example:
        transactions_current_month_1405_06_
        jalali-1405-06-29_
        gregorian-2026-09-20_
        22-48-00.xlsx
    """

    now = timezone.now()

    local_now = timezone.localtime(now) if timezone.is_aware(now) else now

    persian_date = jdatetime.date.fromgregorian(
        date=local_now.date(),
    )

    jalali_stamp = (
        f"{persian_date.year:04d}-"
        f"{persian_date.month:02d}-"
        f"{persian_date.day:02d}"
    )

    gregorian_stamp = (
        f"{local_now.year:04d}-" f"{local_now.month:02d}-" f"{local_now.day:02d}"
    )

    time_stamp = (
        f"{local_now.hour:02d}-" f"{local_now.minute:02d}-" f"{local_now.second:02d}"
    )

    return (
        f"{filename_prefix}_"
        f"jalali-{jalali_stamp}_"
        f"gregorian-{gregorian_stamp}_"
        f"{time_stamp}."
        f"{extension}"
    )


def export_transactions_csv(
    queryset: QuerySet[TransactionModel],
    *,
    filename_prefix: str = "transactions",
):
    """
    Export transactions as CSV.
    """

    filename = _build_export_filename(
        extension="csv",
        filename_prefix=filename_prefix,
    )

    return create_csv_response(
        filename=filename,
        headers=TRANSACTION_HEADERS,
        rows=_transaction_rows(queryset),
    )


def export_transactions_excel(
    queryset: QuerySet[TransactionModel],
    *,
    filename_prefix: str = "transactions",
):
    """
    Export transactions as Excel.
    """

    filename = _build_export_filename(
        extension="xlsx",
        filename_prefix=filename_prefix,
    )

    return create_excel_response(
        filename=filename,
        sheet_name="Transactions",
        headers=TRANSACTION_HEADERS,
        rows=_transaction_rows(queryset),
        number_columns={
            5,
            6,
            10,
            11,
        },
    )
