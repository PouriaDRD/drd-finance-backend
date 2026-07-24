from django.urls import path

from .views import (
    MyCategoriesAPIView,
    MyActiveCategoriesAPIView,
    CategoryCreateAPIView,
    CategoryUpdateAPIView,
    MyTransactionsAPIView,
    PersianMonthSummaryAPIView,
    YearlySummaryAPIView,
)

urlpatterns = [
    path(
        route="my-categories/",
        view=MyCategoriesAPIView.as_view(),
        name="my-categories",
    ),
    path(
        route="my-active-categories/",
        view=MyActiveCategoriesAPIView.as_view(),
        name="my-active-categories",
    ),
    path(
        route="create-category/",
        view=CategoryCreateAPIView.as_view(),
        name="create-category",
    ),
    path(
        route="update-category/<uuid:category_id>/",
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
]
