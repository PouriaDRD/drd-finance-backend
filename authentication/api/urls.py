from django.urls import path


from .views import (
    LoginAPIView,
    RegisterAPIView,
    TokenRefreshAPIView,
    MyLoginHistoryAPIView,
)

urlpatterns = [
    # Login history
    path("my-login-history/", MyLoginHistoryAPIView.as_view(), name="my-login-history"),
    # Normal login
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    # Refresh token
    path("refresh/", TokenRefreshAPIView.as_view(), name="refresh-token"),
]
