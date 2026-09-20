import jdatetime

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import (
    Case,
    IntegerField,
    Sum,
    When,
)
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render
from django.urls import (
    path,
    reverse,
)
from django.utils import timezone
from django.utils.html import format_html

from finance.exports import (
    export_transactions_csv,
    export_transactions_excel,
)
from finance.forms import TransactionImportForm
from finance.imports import TransactionImportService
from finance.models import TransactionModel


def _get_current_persian_period() -> tuple[int, int]:
    """
    Return current Jalali year and month using Django timezone.
    """

    now = timezone.now()

    local_now = timezone.localtime(now) if timezone.is_aware(now) else now

    persian_date = jdatetime.date.fromgregorian(
        date=local_now.date(),
    )

    return (
        persian_date.year,
        persian_date.month,
    )


@admin.register(TransactionModel)
class TransactionAdmin(admin.ModelAdmin):
    change_list_template = "admin/transaction/change_list.html"

    list_display = (
        "user",
        "formatted_amount",
        "type_badge",
        "date",
        "month",
        "year",
        "category",
        "description_short",
    )

    list_filter = (
        "type",
        "month",
        "year",
        "date",
        "category",
    )

    search_fields = (
        "description",
        "user__email",
        "user__name",
        "category__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "user",
        "category",
    )

    ordering = (
        "-date",
        "-created_at",
    )

    list_per_page = 25

    actions = (
        "mark_as_income",
        "mark_as_expense",
        "export_selected_csv",
        "export_selected_excel",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "user",
                    "category",
                ),
            },
        ),
        (
            "Transaction",
            {
                "fields": (
                    "amount",
                    "description",
                    "month",
                    "year",
                    "date",
                ),
            },
        ),
        (
            "Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    # =========================================================
    # Queryset
    # =========================================================

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
                "category",
            )
        )

    # =========================================================
    # Display
    # =========================================================

    @admin.display(
        description="Amount",
        ordering="amount",
    )
    def formatted_amount(self, obj):
        color = "#16a34a" if obj.is_income else "#dc2626"

        amount = f"{obj.amount:,}"

        return format_html(
            """
            <span style="
                color:{};
                font-weight:700;
                font-size:13px;
            ">
                {}
            </span>
            """,
            color,
            amount,
        )

    @admin.display(
        description="Type",
        ordering="type",
    )
    def type_badge(self, obj):
        colors = {
            "income": "#16a34a",
            "expense": "#dc2626",
        }

        color = colors.get(
            obj.type,
            "#6b7280",
        )

        return format_html(
            """
            <span style="
                background:{};
                color:white;
                padding:3px 10px;
                border-radius:999px;
                font-size:11px;
                font-weight:600;
            ">
                {}
            </span>
            """,
            color,
            obj.get_type_display,
        )

    @admin.display(
        description="Description",
    )
    def description_short(self, obj):
        if not obj.description:
            return "—"

        if len(obj.description) <= 40:
            return obj.description

        return f"{obj.description[:40]}..."

    # =========================================================
    # Bulk actions
    # =========================================================

    @admin.action(
        description="Mark selected as Income",
    )
    def mark_as_income(
        self,
        request,
        queryset,
    ):
        updated = queryset.update(
            type="income",
        )

        self.message_user(
            request,
            (f"{updated} transaction(s) " "marked as Income."),
        )

    @admin.action(
        description="Mark selected as Expense",
    )
    def mark_as_expense(
        self,
        request,
        queryset,
    ):
        updated = queryset.update(
            type="expense",
        )

        self.message_user(
            request,
            (f"{updated} transaction(s) " "marked as Expense."),
        )

    @admin.action(
        description=("Export selected transactions as CSV"),
    )
    def export_selected_csv(
        self,
        request,
        queryset,
    ):
        queryset = queryset.select_related(
            "user",
            "category",
        )

        return export_transactions_csv(
            queryset,
            filename_prefix=("transactions_selected"),
        )

    @admin.action(
        description=("Export selected transactions as Excel"),
    )
    def export_selected_excel(
        self,
        request,
        queryset,
    ):
        queryset = queryset.select_related(
            "user",
            "category",
        )

        return export_transactions_excel(
            queryset,
            filename_prefix=("transactions_selected"),
        )

    # =========================================================
    # Dashboard summary
    # =========================================================

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):
        extra_context = extra_context or {}

        queryset = self.get_queryset(
            request,
        )

        totals = queryset.aggregate(
            income_total=Sum(
                Case(
                    When(
                        type="income",
                        then="amount",
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
            ),
            expense_total=Sum(
                Case(
                    When(
                        type="expense",
                        then="amount",
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
            ),
        )

        income = totals["income_total"] or 0

        expense = totals["expense_total"] or 0

        current_year, current_month = _get_current_persian_period()

        current_month_name = TransactionModel(
            year=current_year,
            month=current_month,
        ).get_persian_month_name()

        extra_context.update(
            {
                "income_total": (f"{income:,}"),
                "expense_total": (f"{expense:,}"),
                "balance_total": (f"{income - abs(expense):,}"),
                "import_url": reverse(
                    ("admin:" "finance_transaction_import"),
                ),
                ("export_current_month_" "csv_url"): reverse(
                    ("admin:" "finance_transaction_" "export_current_month_csv"),
                ),
                ("export_current_month_" "excel_url"): reverse(
                    ("admin:" "finance_transaction_" "export_current_month_excel"),
                ),
                "current_persian_year": (current_year),
                "current_persian_month": (current_month),
                "current_persian_month_name": (current_month_name),
            },
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    # =========================================================
    # Custom URLs
    # =========================================================

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "import/",
                self.admin_site.admin_view(
                    self.import_view,
                ),
                name=("finance_transaction_import"),
            ),
            path(
                ("export/current-month/" "csv/"),
                self.admin_site.admin_view(
                    self.export_current_month_csv_view,
                ),
                name=("finance_transaction_" "export_current_month_csv"),
            ),
            path(
                ("export/current-month/" "excel/"),
                self.admin_site.admin_view(
                    self.export_current_month_excel_view,
                ),
                name=("finance_transaction_" "export_current_month_excel"),
            ),
        ]

        return custom_urls + urls

    # =========================================================
    # Current month export
    # =========================================================

    def _get_current_month_queryset(
        self,
        request: HttpRequest,
    ):
        year, month = _get_current_persian_period()

        queryset = (
            self.get_queryset(request)
            .filter(
                year=year,
                month=month,
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

        return (
            queryset,
            year,
            month,
        )

    def export_current_month_csv_view(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        """
        Export all current-month transactions
        available to Django Admin.
        """

        if not self.has_view_permission(
            request,
        ):
            raise PermissionDenied

        queryset, year, month = self._get_current_month_queryset(
            request,
        )

        return export_transactions_csv(
            queryset,
            filename_prefix=("transactions_current_month_" f"{year}_{month:02d}"),
        )

    def export_current_month_excel_view(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        """
        Export all current-month transactions
        available to Django Admin.
        """

        if not self.has_view_permission(
            request,
        ):
            raise PermissionDenied

        queryset, year, month = self._get_current_month_queryset(
            request,
        )

        return export_transactions_excel(
            queryset,
            filename_prefix=("transactions_current_month_" f"{year}_{month:02d}"),
        )

    # =========================================================
    # Import
    # =========================================================

    def import_view(
        self,
        request: HttpRequest,
    ):
        if not self.has_add_permission(
            request,
        ):
            raise PermissionDenied

        result = None

        form = TransactionImportForm()

        if request.method == "POST":
            form = TransactionImportForm(
                request.POST,
                request.FILES,
            )

            if form.is_valid():
                uploaded_file = form.cleaned_data["file"]

                filename = uploaded_file.name.lower()

                try:
                    if filename.endswith(
                        ".csv",
                    ):
                        result = TransactionImportService.import_csv(
                            user=request.user,
                            file=uploaded_file,
                        )

                    elif filename.endswith(
                        ".xlsx",
                    ):
                        result = TransactionImportService.import_excel(
                            user=request.user,
                            file=uploaded_file,
                        )

                except Exception as exc:
                    form.add_error(
                        "file",
                        ("خطا در پردازش فایل: " f"{exc}"),
                    )

        context = {
            **self.admin_site.each_context(
                request,
            ),
            "title": ("Import Transactions"),
            "form": form,
            "result": result,
            "opts": self.model._meta,
        }

        return render(
            request,
            ("admin/transaction/" "import.html"),
            context,
        )
