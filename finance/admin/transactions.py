from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Case, When, IntegerField, Count

from finance.models import TransactionModel


@admin.register(TransactionModel)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "formatted_amount",
        "type_badge",
        "date",
        "month",
        "category",
        "description_short",
    )

    list_filter = (
        "type",
        "month",
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

    list_per_page = 100

    save_on_top = True

    actions = (
        "mark_as_income",
        "mark_as_expense",
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
                    "type",
                    "amount",
                    "description",
                    "month",
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
            obj.get_type_display(),
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
                "balance_total": f"{income - expense:,}",
            }
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )
