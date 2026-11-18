from django.urls import path

from .views import (
    departments_analytics,
    gaps_analytics,
    overview_analytics,
    skills_analytics,
)

urlpatterns = [
    path("analytics/overview/", overview_analytics, name="analytics-overview"),
    path("analytics/skills/", skills_analytics, name="analytics-skills"),
    path("analytics/gaps/", gaps_analytics, name="analytics-gaps"),
    path(
        "analytics/departments/",
        departments_analytics,
        name="analytics-departments",
    ),
]
