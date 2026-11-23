"""API views for analytics dashboard (thin adapters over aggregator)."""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.employees.models import Department, Employee
from apps.projects.models import Project
from apps.skills.models import EmployeeSkill

from apps.gap_analysis.services.analyzer import employee_gap

from .services.aggregator import (
    department_capacity_summary,
    department_skill_coverage,
    proficiency_distribution,
    top_gaps_across_projects,
)


# ---- helpers ---------------------------------------------------------------

def _employee_skill_rows() -> list[dict]:
    return [
        {
            "employee_id": str(es.employee_id),
            "skill_id": str(es.skill_id),
            "skill_name": es.skill.name,
            "proficiency": es.proficiency,
            "is_verified": es.is_verified,
        }
        for es in EmployeeSkill.objects.select_related("skill")
    ]


def _department_dicts() -> list[dict]:
    return [
        {
            "department_id": str(d.id),
            "department_name": d.name,
            "employee_ids": [str(e.id) for e in d.employees.all()],
        }
        for d in Department.objects.all()
    ]


def _employee_dicts() -> list[dict]:
    return [
        {
            "employee_id": str(e.id),
            "department_id": str(e.department_id),
            "total_experience_years": e.total_experience_years,
        }
        for e in Employee.objects.all()
    ]


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


# ---- endpoints -------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def skills_analytics(request):
    dept_id = request.query_params.get("department")
    rows = _employee_skill_rows()
    if dept_id:
        get_object_or_404(Department, pk=dept_id)
        member_ids = {
            str(e.id) for e in Employee.objects.filter(department_id=dept_id)
        }
        rows = [r for r in rows if r["employee_id"] in member_ids]
    return Response(proficiency_distribution(rows))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def gaps_analytics(request):
    active = Project.objects.filter(status=Project.Status.ACTIVE)
    reports = []
    for project in active:
        reqs = _requirements_for(project)
        for emp in Employee.objects.all(): # Check gaps for ALL employees
            gap = employee_gap(reqs, _held_for(emp))
            reports.append(
                {
                    "project_id": str(project.id),
                    "project_name": project.name,
                    "gap": gap,
                }
            )
    return Response(
        {
            "project_count": active.count(),
            "top_gaps": top_gaps_across_projects(reports),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def departments_analytics(request):
    return Response(
        {
            "departments": department_capacity_summary(
                _department_dicts(), _employee_dicts(), _employee_skill_rows()
            )
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def overview_analytics(request):
    departments = _department_dicts()
    employees = _employee_dicts()
    skill_rows = _employee_skill_rows()

    dist = proficiency_distribution(skill_rows)
    capacity = department_capacity_summary(departments, employees, skill_rows)

    active = Project.objects.filter(status=Project.Status.ACTIVE)
    reports = []
    for project in active:
        reqs = _requirements_for(project)
        for emp in Employee.objects.all():
            reports.append(
                {
                    "project_id": str(project.id),
                    "project_name": project.name,
                    "gap": employee_gap(reqs, _held_for(emp)),
                }
            )
    top_gaps = top_gaps_across_projects(reports, limit=5)

    return Response(
        {
            "headcount": Employee.objects.count(), # <-- FIXED: Shows ALL employees
            "department_count": Department.objects.count(),
            "project_count": Project.objects.count(),
            "active_project_count": active.count(),
            "proficiency_by_band": dist["by_band"],
            "top_skills": dist["by_skill"][:5],
            "top_gaps": top_gaps,
            "departments": capacity,
        }
    )