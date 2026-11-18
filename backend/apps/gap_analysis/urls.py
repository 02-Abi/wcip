from django.urls import path

from .views import department_skill_gap, employee_skill_gap

urlpatterns = [
    path(
        "employees/<uuid:employee_id>/skill-gap/",
        employee_skill_gap,
        name="employee-skill-gap",
    ),
    path(
        "departments/<uuid:department_id>/skill-gap/",
        department_skill_gap,
        name="department-skill-gap",
    ),
]
