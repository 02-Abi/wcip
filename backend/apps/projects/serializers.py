from rest_framework import serializers
from .models import Project, ProjectRequiredSkill


class ProjectSerializer(serializers.ModelSerializer):
    required_skills_count = serializers.IntegerField(source="required_skills.count", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "status", "priority",
            "start_date", "end_date", "headcount_needed",
            "required_skills_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "required_skills_count", "created_at", "updated_at"]

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError("end_date cannot be before start_date.")
        hc = attrs.get("headcount_needed")
        if hc is not None and hc < 1:
            raise serializers.ValidationError("headcount_needed must be >= 1.")
        return attrs


class ProjectRequiredSkillSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    skill_category = serializers.CharField(source="skill.category.name", read_only=True)

    class Meta:
        model = ProjectRequiredSkill
        fields = [
            "id", "project", "project_name", "skill", "skill_name", "skill_category",
            "minimum_proficiency", "minimum_years", "is_mandatory", "weight",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "project_name", "skill_name", "skill_category", "created_at", "updated_at"]

    def validate_minimum_years(self, value):
        if value < 0:
            raise serializers.ValidationError("minimum_years cannot be negative.")
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("weight must be > 0.")
        return value
