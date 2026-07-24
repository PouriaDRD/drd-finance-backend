from django.contrib import admin
from django.conf import settings
from rest_framework import routers
from django.urls import path, include
from django.conf.urls.static import static

from config.settings.app_config import config

router = routers.DefaultRouter()

base_url = config.app.base_url
admin_url = config.app.admin_url

urlpatterns = [
    path(base_url, include(router.urls)),
    # Admin URL without base_url
    path(base_url + admin_url, admin.site.urls),
    # API v1 routes
    path(base_url + "accounts/", include("accounts.api.urls")),
    path(base_url + "authentication/", include("authentication.api.urls")),
    path(base_url + "finance/", include("finance.api.urls")),
]


if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.index_title = "DRD Finance Admin"
admin.site.site_header = "DRD Finance Admin"
admin.site.site_title = "DRD Finance"
