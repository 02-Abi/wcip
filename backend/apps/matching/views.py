from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.employees.models import Employee
from apps.projects.models import Project
from .services.matcher import find_matches_for_project


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def project_matches(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    try:
        top_n = int(request.query_params.get("top", "20"))
    except ValueError:
        top_n = 20
    if top_n < 1 or top_n > 100:
        top_n = 20

    results = find_matches_for_project(
        project,
        Employee.objects.all(),
        top_n=top_n,
    )
    return Response({
        "project_id": str(project.id),
        "project_name": project.name,
        "count": len(results),
        "matches": results,
    })
