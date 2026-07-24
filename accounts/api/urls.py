from django.urls import path

from .views import UserAPIView

urlpatterns = [
    path("me/", UserAPIView.as_view(), name="user-view"),
]
