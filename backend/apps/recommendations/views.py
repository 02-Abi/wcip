"""API views for learning recommendations (thin adapters over engine)."""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.employees.models import Department, Employee
from apps.projects.models import Project
from apps.skills.models import EmployeeSkill, Skill

from apps.gap_analysis.services.analyzer import department_gap, employee_gap

from .services.engine import recommend_for_department, recommend_for_employee


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


def _catalog() -> dict[str, list[str]]:
    """skill_id -> names of other skills in the same category."""
    by_category: dict[str, list[tuple[str, str]]] = {}
    for skill in Skill.objects.select_related("category").filter(is_active=True):
        by_category.setdefault(str(skill.category_id), []).append(
            (str(skill.id), skill.name)
        )
    catalog: dict[str, list[str]] = {}
    for members in by_category.values():
        for skill_id, _ in members:
            catalog[skill_id] = [name for sid, name in members if sid != skill_id]
    return catalog


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
def employee_recommendations(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    project, err = _require_project(request)
    if err:
        return err

    gap = employee_gap(_requirements_for(project), _held_for(employee))
    recs = recommend_for_employee(gap, _catalog())
    return Response(
        {
            "employee_id": str(employee.id),
            "employee_name": employee.full_name,
            "project_id": str(project.id),
            "project_name": project.name,
            "coverage_pct": gap["coverage_pct"],
            "fully_qualified": gap["fully_qualified"],
            "recommendation_count": len(recs),
            "recommendations": recs,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def department_recommendations(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    project, err = _require_project(request)
    if err:
        return err

    employees = [
        {
            "employee_id": emp.id,
            "full_name": emp.full_name,
            "held_by_skill": _held_for(emp),
        }
        for emp in department.employees.all()
    ]
    gap = department_gap(_requirements_for(project), employees)
    result = recommend_for_department(gap, _catalog())
    return Response(
        {
            "department_id": str(department.id),
            "department_name": department.name,
            "project_id": str(project.id),
            "project_name": project.name,
            "overall_coverage_pct": gap["overall_coverage_pct"],
            **result,
        }
    )
