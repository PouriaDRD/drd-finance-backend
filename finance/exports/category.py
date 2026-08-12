from datetime import datetime

from django.db.models import QuerySet

from .csv import create_csv_response
from .excel import create_excel_response
from finance.models import CategoryModel

CATEGORY_HEADERS = [
    "شناسه",
    "ایمیل کاربر",
    "نام",
    "نوع",
    "توضیحات",
    "آرشیو شده",
    "تعداد تراکنش‌ها",
    "رنگ",
    "تاریخ ایجاد",
    "آخرین بروزرسانی",
]


def _category_rows(queryset: QuerySet[CategoryModel]):
    """
    Convert categories into export rows.
    """

    for category in queryset:
        yield [
            str(category.id),
            category.user.email if category.user else "",
            category.name,
            category.get_type_display,
            category.description or "",
            "بله" if category.is_archived else "خیر",
            getattr(
                category,
                "_transaction_count",
                category.transactions.count(),  # type: ignore
            ),
            category.color,
            (
                category.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if category.created_at
                else ""
            ),
            (
                category.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if category.updated_at
                else ""
            ),
        ]


def export_categories_csv(queryset: QuerySet):
    """
    Export categories as CSV.
    """

    filename = f"categories_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return create_csv_response(
        filename=filename,
        headers=CATEGORY_HEADERS,
        rows=_category_rows(queryset),
    )


def export_categories_excel(queryset: QuerySet):
    """
    Export categories as Excel.
    """

    filename = f"categories_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return create_excel_response(
        filename=filename,
        sheet_name="Categories",
        headers=CATEGORY_HEADERS,
        rows=_category_rows(queryset),
        number_columns={
            6,  # transaction count
        },
    )
