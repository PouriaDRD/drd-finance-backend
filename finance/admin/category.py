from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from finance.models import CategoryModel


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "type_badge",
        "color_display",
        "is_archived",
        "transaction_count",
        "created_at",
    )

    list_filter = (
        "type",
        "is_archived",
        "created_at",
    )

    search_fields = (
        "name",
        "user__email",
        "user__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = [
        "-created_at",
    ]

    autocomplete_fields = ("user",)

    list_per_page = 25

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "user",
                    "name",
                    "type",
                    "description",
                )
            },
        ),
        (
            "Appearance",
            {
                "fields": (
                    "icon",
                    "color",
                )
            },
        ),
        (
            "Settings",
            {
                "fields": ("is_archived",),
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related(
            "user",
        ).annotate(_transaction_count=Count("transactions"))

    @admin.display(description="Transactions", ordering="_transaction_count")
    def transaction_count(self, obj):
        return obj._transaction_count

    @admin.display(description="Color")
    def color_display(self, obj):
        return format_html(
            """
            <div style="
                width:12px;
                height:12px;
                border-radius:50%;
                background:{};
                border:1px solid #ddd;
            "></div>
            """,
            obj.color,
        )

    @admin.display(description="Type", ordering="type")
    def type_badge(self, obj):
        colors = {
            "income": "#106e33",
            "expense": "#6D1818",
        }

        color = colors.get(obj.type, "#6b7280")

        return format_html(
            """
            <span style="
                background:{};
                color:white;
                padding:2px 8px;
                border-radius:8px;
                font-size:12px;
                font-weight:600;
            ">
                {}
            </span>
            """,
            color,
            obj.get_type_display(),
        )

    actions = (
        "archive_selected",
        "unarchive_selected",
        "mark_as_income",
        "mark_as_expense",
    )

    @admin.action(description="Archive selected categories")
    def archive_selected(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(
            request,
            f"{updated} category(ies) archived successfully.",
        )

    @admin.action(description="Unarchive selected categories")
    def unarchive_selected(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(
            request,
            f"{updated} category(ies) unarchived successfully.",
        )

    @admin.action(description="Mark selected as Income")
    def mark_as_income(self, request, queryset):
        updated = queryset.update(type="income")
        self.message_user(
            request,
            f"{updated} category(ies) marked as Income.",
        )

    @admin.action(description="Mark selected as Expense")
    def mark_as_expense(self, request, queryset):
        updated = queryset.update(type="expense")
        self.message_user(
            request,
            f"{updated} category(ies) marked as Expense.",
        )
