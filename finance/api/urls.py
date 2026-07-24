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
)

urlpatterns = [
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
    path(
        route="my-transactions/",
        view=MyTransactionsAPIView.as_view(),
        name="my-transactions",
    ),
    path(
        "my-transactions/summary/<int:year>/<int:month>/",
        PersianMonthSummaryAPIView.as_view(),
        name="transaction-month-summary",
    ),
    path(
        "my-transactions/summary/<int:year>/",
        YearlySummaryAPIView.as_view(),
        name="transaction-yearly-summary",
    ),
    # Create transaction
    path(
        "my-transactions/create/",
        TransactionCreateAPIView.as_view(),
        name="transaction-create",
    ),
    # Update transaction
    path(
        "my-transactions/<uuid:transaction_id>/update/",
        TransactionUpdateAPIView.as_view(),
        name="transaction-update",
    ),
    # Delete transaction
    path(
        "my-transactions/<uuid:transaction_id>/delete/",
        TransactionDeleteAPIView.as_view(),
        name="transaction-delete",
    ),
]
