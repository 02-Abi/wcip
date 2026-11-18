"""DRF viewset mixin that writes audit events on CUD operations.

Usage: add to a ModelViewSet's bases and set the two class attributes:

    class EmployeeViewSet(AuditedModelViewSet, viewsets.ModelViewSet):
        audit_entity_type = "employee"
        audit_fields = ["first_name", "last_name", "email", "designation"]

For UPDATE we snapshot ``audit_fields`` before the change (in
``perform_update`` via the pre-save instance) and diff against after.
"""

from __future__ import annotations

from .logger import log_create, log_delete, log_update, snapshot


class AuditedModelViewSet:
    audit_entity_type: str = ""
    audit_fields: list[str] = []

    # -- hooks ---------------------------------------------------------------

    def perform_create(self, serializer):
        instance = serializer.save()
        log_create(
            actor=self.request.user,
            instance=instance,
            entity_type=self.audit_entity_type,
            fields=self.audit_fields,
        )
        return instance

    def perform_update(self, serializer):
        instance = serializer.instance
        before = snapshot(instance, self.audit_fields)
        instance = serializer.save()
        log_update(
            actor=self.request.user,
            instance=instance,
            entity_type=self.audit_entity_type,
            before=before,
            fields=self.audit_fields,
        )
        return instance

    def perform_destroy(self, instance):
        log_delete(
            actor=self.request.user,
            instance=instance,
            entity_type=self.audit_entity_type,
            fields=self.audit_fields,
        )
        instance.delete()
