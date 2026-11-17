from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import SkillCategory, Skill, EmployeeSkill
from .serializers import SkillCategorySerializer, SkillSerializer, EmployeeSkillSerializer


class SkillCategoryViewSet(viewsets.ModelViewSet):
    queryset = SkillCategory.objects.all().order_by("name")
    serializer_class = SkillCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.select_related("category").all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["name", "category", "created_at"]
    ordering = ["category__name", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        cat = self.request.query_params.get("category")
        if cat:
            qs = qs.filter(category_id=cat)
        active = self.request.query_params.get("is_active")
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ("1", "true", "yes"))
        return qs


class EmployeeSkillViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSkill.objects.select_related("employee", "skill", "skill__category").all()
    serializer_class = EmployeeSkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["employee__first_name", "employee__last_name", "skill__name"]
    ordering_fields = ["proficiency", "years_experience", "created_at"]
    ordering = ["-proficiency", "skill__name"]

    def get_queryset(self):
        qs = super().get_queryset()
        emp = self.request.query_params.get("employee")
        if emp:
            qs = qs.filter(employee_id=emp)
        skill = self.request.query_params.get("skill")
        if skill:
            qs = qs.filter(skill_id=skill)
        return qs
