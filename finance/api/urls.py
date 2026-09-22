from django.urls import path

from .views import (
    MyCategoriesAPIView,
    MyActiveCategoriesAPIView,
    CategoryCreateAPIView,
    CategoryUpdateAPIView,
    MyTransactionsAPIView,
    PersianMonthSummaryAPIView,
    YearlySummaryAPIView,
    TransactionCreateAPIView,
    TransactionUpdateAPIView,
    TransactionDeleteAPIView,
    PersianMonthTransactionsExportAPIView,
)


urlpatterns = [
    # =========================================================
    # Categories
    # =========================================================
    path(
        route="my-categories/",
        view=MyCategoriesAPIView.as_view(),
        name="my-categories",
    ),
    path(
        route="my-categories/active/",
        view=MyActiveCategoriesAPIView.as_view(),
        name="my-active-categories",
    ),
    path(
        route="my-categories/create/",
        view=CategoryCreateAPIView.as_view(),
        name="create-category",
    ),
    path(
        route="my-categories/<uuid:category_id>/update/",
        view=CategoryUpdateAPIView.as_view(),
        name="update-category",
    ),

    # =========================================================
    # Transactions
    # =========================================================
    path(
        route="my-transactions/",
        view=MyTransactionsAPIView.as_view(),
        name="my-transactions",
    ),

    # =========================================================
    # Transaction Reports
    # =========================================================
    path(
        route="my-transactions/summary/<int:year>/<int:month>/",
        view=PersianMonthSummaryAPIView.as_view(),
        name="transaction-month-summary",
    ),
    path(
        route="my-transactions/summary/<int:year>/",
        view=YearlySummaryAPIView.as_view(),
        name="transaction-yearly-summary",
    ),

    # =========================================================
    # Transaction Export
    # =========================================================
    path(
        route=(
            "my-transactions/export/"
            "<int:year>/<int:month>/<str:file_type>/"
        ),
        view=PersianMonthTransactionsExportAPIView.as_view(),
        name="transaction-month-export",
    ),

    # =========================================================
    # Transaction CRUD
    # =========================================================
    path(
        route="my-transactions/create/",
        view=TransactionCreateAPIView.as_view(),
        name="transaction-create",
    ),
    path(
        route="my-transactions/<uuid:transaction_id>/update/",
        view=TransactionUpdateAPIView.as_view(),
        name="transaction-update",
    ),
    path(
        route="my-transactions/<uuid:transaction_id>/delete/",
        view=TransactionDeleteAPIView.as_view(),
        name="transaction-delete",
    ),
]
