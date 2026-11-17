from rest_framework import serializers
from .models import SkillCategory, Skill, EmployeeSkill


class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    class Meta:
        model = Skill
        fields = ["id", "category", "category_name", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "category_name", "created_at", "updated_at"]


class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    skill_category = serializers.CharField(source="skill.category.name", read_only=True)
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = [
            "id", "employee", "employee_id", "skill", "skill_name", "skill_category",
            "proficiency", "years_experience", "last_used", "is_verified",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "employee_id", "skill_name", "skill_category", "created_at", "updated_at"]

    def validate_years_experience(self, value):
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        return value
