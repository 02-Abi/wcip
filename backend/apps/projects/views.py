from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Project, ProjectRequiredSkill
from .serializers import ProjectSerializer, ProjectRequiredSkillSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "priority", "status", "start_date", "created_at"]
    ordering = ["-priority", "-created_at"]


class ProjectRequiredSkillViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequiredSkill.objects.select_related("project", "skill", "skill__category").all()
    serializer_class = ProjectRequiredSkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["project", "skill", "minimum_proficiency", "is_mandatory"]
    search_fields = ["project__name", "skill__name"]
    ordering_fields = ["weight", "minimum_years", "created_at"]
    ordering = ["-weight", "skill__name"]
