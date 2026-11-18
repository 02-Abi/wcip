from django.urls import path

from .views import department_recommendations, employee_recommendations

urlpatterns = [
    path(
        "employees/<uuid:employee_id>/recommendations/",
        employee_recommendations,
        name="employee-recommendations",
    ),
    path(
        "departments/<uuid:department_id>/recommendations/",
        department_recommendations,
        name="department-recommendations",
    ),
]
