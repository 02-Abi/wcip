"""Employee and Department models.

Multi-tenancy note: the current shape has no organization FK yet —
that lands in Phase 4. It is easier to add it later (with a migration
that backfills a default org) than to retrofit everything now.
"""
import uuid
from django.db import models


class Department(models.Model):
    """A department within the (eventual) organization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Employee(models.Model):
    """A single employee profile."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On leave"
        TERMINATED = "TERMINATED", "Terminated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="employees"
    )
    designation = models.CharField(max_length=120)
    joining_date = models.DateField()
    employment_status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    total_experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name"]
        indexes = [
            models.Index(fields=["department", "employment_status"]),
            models.Index(fields=["employee_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()