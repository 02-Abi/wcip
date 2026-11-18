from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("common.urls")),
    path("api/auth/", include("common.auth_urls")),
    path("api/", include("apps.employees.urls")),
    path("api/", include("apps.skills.urls")),
    path("api/", include("apps.projects.urls")),
    path("api/", include("apps.matching.urls")),
    path("api/", include("apps.gap_analysis.urls")),
        path("api/", include("apps.recommendations.urls")),
]