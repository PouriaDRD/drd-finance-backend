from django.urls import path

from .views import (
    MyCategoriesAPIView,
    MyActiveCategoriesAPIView,
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
]
