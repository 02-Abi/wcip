"""Employee and Department CRUD + filtering/search/ordering."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.audit.services.mixins import AuditedModelViewSet
from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]


class EmployeeViewSet(AuditedModelViewSet, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("department").all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    audit_entity_type = "employee"
    audit_fields = [
        "employee_id", "first_name", "last_name", "email", "department_id",
        "designation", "joining_date", "employment_status", "total_experience_years",
    ]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["department", "employment_status"]
    search_fields = ["first_name", "last_name", "email", "employee_id", "designation"]
    ordering_fields = ["first_name", "last_name", "joining_date", "total_experience_years", "created_at"]
    ordering = ["first_name", "last_name"]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        code = self.request.query_params.get("department_code")
        if code:
            qs = qs.filter(department__code__iexact=code)
        min_exp = self.request.query_params.get("min_experience")
        if min_exp:
            try:
                qs = qs.filter(total_experience_years__gte=float(min_exp))
            except ValueError:
                pass
        return qs