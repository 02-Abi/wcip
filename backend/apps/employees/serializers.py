"""Employee and Department serializers."""
from rest_framework import serializers
from .models import Department, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "department",
            "department_name",
            "designation",
            "joining_date",
            "employment_status",
            "total_experience_years",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_name", "department_name"]

    def validate_total_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError("Total experience cannot be negative.")
        return value

    def validate(self, attrs):
        # Unique composite: employee_id and email are unique per model already.
        # Add early validation here as needed (e.g., department existence).
        return attrs