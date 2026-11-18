"""API views for skill-gap analysis (thin adapters over analyzer)."""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.employees.models import Department, Employee
from apps.projects.models import Project
from apps.skills.models import EmployeeSkill

from .services.analyzer import department_gap, employee_gap


def _requirements_for(project: Project) -> list[dict]:
    return [
        {
            "skill_id": str(r.skill_id),
            "skill_name": r.skill.name,
            "minimum_proficiency": r.minimum_proficiency,
            "minimum_years": r.minimum_years,
            "is_mandatory": r.is_mandatory,
            "weight": r.weight,
        }
        for r in project.required_skills.select_related("skill")
    ]


def _held_for(employee: Employee) -> dict[str, dict]:
    return {
        str(es.skill_id): {
            "proficiency": es.proficiency,
            "years_experience": es.years_experience,
        }
        for es in EmployeeSkill.objects.filter(employee=employee)
    }


def _require_project(request):
    project_id = request.query_params.get("project")
    if not project_id:
        return None, Response(
            {"detail": "query parameter 'project' is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    project = get_object_or_404(Project, pk=project_id)
    return project, None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employee_skill_gap(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    project, err = _require_project(request)
    if err:
        return err

    result = employee_gap(_requirements_for(project), _held_for(employee))
    return Response(
        {
            "employee_id": str(employee.id),
            "employee_name": employee.full_name,
            "project_id": str(project.id),
            "project_name": project.name,
            **result,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def department_skill_gap(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    project, err = _require_project(request)
    if err:
        return err

    employees = []
    for emp in department.employees.all():
        employees.append(
            {
                "employee_id": emp.id,
                "full_name": emp.full_name,
                "held_by_skill": _held_for(emp),
            }
        )

    result = department_gap(_requirements_for(project), employees)
    return Response(
        {
            "department_id": str(department.id),
            "department_name": department.name,
            "project_id": str(project.id),
            "project_name": project.name,
            **result,
        }
    )
