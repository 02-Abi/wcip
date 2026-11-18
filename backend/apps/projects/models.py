"""Project and project-skill-requirement models.

These are the inputs the matching engine (Phase 9) will compare against
EmployeeSkill records. They deliberately contain no computed fields —
the matching engine owns all scoring logic in a separate pure-Python service.
"""
import uuid
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        ACTIVE = "ACTIVE", "Active"
        ON_HOLD = "ON_HOLD", "On hold"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PLANNED)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIUM)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    headcount_needed = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [models.Index(fields=["status", "priority"])]

    def __str__(self) -> str:
        return self.name


class ProjectRequiredSkill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        EXPERT = "EXPERT", "Expert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="required_skills")
    skill = models.ForeignKey(
        "skills.Skill", on_delete=models.PROTECT, related_name="project_requirements"
    )
    minimum_proficiency = models.CharField(
        max_length=16, choices=Proficiency.choices, default=Proficiency.INTERMEDIATE
    )
    minimum_years = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    is_mandatory = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "skill"], name="uniq_project_skill"),
        ]
        ordering = ["-weight", "skill__name"]
        indexes = [models.Index(fields=["skill", "minimum_proficiency"])]

    def __str__(self) -> str:
        return f"{self.project.name} · {self.skill.name} ({self.minimum_proficiency})"
