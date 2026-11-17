from django.contrib import admin
from .models import SkillCategory, Skill, EmployeeSkill


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active", "created_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["name"]


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ["employee", "skill", "proficiency", "years_experience", "is_verified"]
    list_filter = ["proficiency", "is_verified", "skill__category"]
    search_fields = ["employee__employee_id", "employee__first_name", "skill__name"]
