from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("common.urls")),
    path("api/auth/", include("common.auth_urls")),
    path("api/", include("apps.employees.urls")),
]