from django.contrib import admin
from .models import Project, ProjectRequiredSkill


class ProjectRequiredSkillInline(admin.TabularInline):
    model = ProjectRequiredSkill
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "priority", "headcount_needed", "start_date", "end_date"]
    list_filter = ["status", "priority"]
    search_fields = ["name", "description"]
    inlines = [ProjectRequiredSkillInline]


@admin.register(ProjectRequiredSkill)
class ProjectRequiredSkillAdmin(admin.ModelAdmin):
    list_display = ["project", "skill", "minimum_proficiency", "minimum_years", "is_mandatory", "weight"]
    list_filter = ["minimum_proficiency", "is_mandatory"]
    search_fields = ["project__name", "skill__name"]
