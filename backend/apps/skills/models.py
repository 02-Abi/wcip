"""Skill taxonomy and employee-skill linkage."""
import uuid
from django.db import models


class SkillCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Skill categories"

    def __str__(self) -> str:
        return self.name


class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(SkillCategory, on_delete=models.PROTECT, related_name="skills")
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__name", "name"]
        constraints = [models.UniqueConstraint(fields=["category", "name"], name="uniq_skill_per_category")]
        indexes = [models.Index(fields=["category", "name"])]

    def __str__(self) -> str:
        return f"{self.category.name} / {self.name}"


class EmployeeSkill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        EXPERT = "EXPERT", "Expert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="employee_links")
    proficiency = models.CharField(max_length=16, choices=Proficiency.choices, default=Proficiency.BEGINNER)
    years_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    last_used = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["employee", "skill"], name="uniq_employee_skill")]
        ordering = ["-proficiency", "skill__name"]
        indexes = [models.Index(fields=["skill", "proficiency"])]

    def __str__(self) -> str:
        return f"{self.employee.employee_id} · {self.skill.name} ({self.proficiency})"
