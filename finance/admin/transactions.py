from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.utils.html import format_html
from django.http import HttpResponse, HttpRequest
from django.db.models import Sum, Case, When, IntegerField, Count

from finance.models import TransactionModel
from finance.exports import (
    export_transactions_csv,
    export_transactions_excel,
)
from finance.forms import TransactionImportForm
from finance.imports import TransactionImportService


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
                )
            },
        ),
        (
            "Transaction",
            {
                "fields": (
                    # "type",
                    "amount",
                    "description",
                    "month",
                    "year",
                    "date",
                )
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

    # --------------------------------------------------
    # Query Optimization
    # --------------------------------------------------

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
                "category",
            )
            .annotate(transaction_total=Count("id"))
        )

    # --------------------------------------------------
    # Display
    # --------------------------------------------------

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

    @admin.display(description="Description")
    def description_short(self, obj):
        if not obj.description:
            return "—"

        if len(obj.description) <= 40:
            return obj.description

        return f"{obj.description[:40]}..."

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    @admin.action(description="Mark selected as Income")
    def mark_as_income(self, request, queryset):
        updated = queryset.update(type="income")

        self.message_user(
            request,
            f"{updated} transaction(s) marked as Income.",
        )

    @admin.action(description="Mark selected as Expense")
    def mark_as_expense(self, request, queryset):
        updated = queryset.update(type="expense")

        self.message_user(
            request,
            f"{updated} transaction(s) marked as Expense.",
        )

    @admin.action(description="Export selected transactions as CSV")
    def export_selected_csv(self, request, queryset):
        queryset = queryset.select_related(
            "user",
            "category",
        )

        return export_transactions_csv(queryset)

    @admin.action(description="Export selected transactions as Excel")
    def export_selected_excel(self, request, queryset):
        queryset = queryset.select_related(
            "user",
            "category",
        )

        return export_transactions_excel(queryset)

    # --------------------------------------------------
    # Dashboard Summary
    # --------------------------------------------------

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):

        extra_context = extra_context or {}

        totals = self.get_queryset(request).aggregate(
            income_total=Sum(
                Case(
                    When(
                        type="income",
                        then="amount",
                    ),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            expense_total=Sum(
                Case(
                    When(
                        type="expense",
                        then="amount",
                    ),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )

        income = totals["income_total"] or 0

        expense = totals["expense_total"] or 0

        extra_context.update(
            {
                "income_total": f"{income:,}",
                "expense_total": f"{expense:,}",
                "balance_total": (f"{income - abs(expense):,}"),
                # Important:
                # This can be used by your change-list
                # template/button later.
                "import_url": ("import/"),
            }
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    # =====================================================
    # URLs
    # =====================================================

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "import/",
                self.admin_site.admin_view(self.import_view),
                name=("finance_transaction_import"),
            ),
        ]

        return custom_urls + urls

    # =====================================================
    # Import View
    # =====================================================

    def import_view(
        self,
        request: HttpRequest,
    ):

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

                    if filename.endswith(".csv"):

                        result = TransactionImportService.import_csv(
                            user=request.user,
                            file=uploaded_file,
                        )

                    elif filename.endswith(".xlsx"):

                        result = TransactionImportService.import_excel(
                            user=request.user,
                            file=uploaded_file,
                        )

                except Exception as exc:

                    form.add_error(
                        "file",
                        f"خطا در پردازش فایل: {exc}",
                    )

        context = {
            **self.admin_site.each_context(request),
            "title": "Import Transactions",
            "form": form,
            "result": result,
            "opts": self.model._meta,
        }

        return render(
            request,
            "admin/transaction/import.html",
            context,
        )
