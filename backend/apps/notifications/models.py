"""In-app notification inbox."""

import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        GAP_ALERT = "GAP_ALERT", "Skill gap alert"
        RECOMMENDATION = "RECOMMENDATION", "Learning recommendation"
        MATCH_FOUND = "MATCH_FOUND", "Match found"
        SYSTEM = "SYSTEM", "System message"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=32, choices=Kind.choices)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.kind} -> {self.recipient_id}: {self.title}"
