"""Audit logging helpers.

``diff`` is pure Python and fully unit-tested. The ``log_*`` functions
are thin DB writers. Views call these; nothing else should.
"""

from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Any

from apps.audit.models import AuditEvent


# ---- pure helpers ----------------------------------------------------------

def _normalize(value: Any) -> Any:
    """Make values JSON-serializable and comparable."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    return value


def diff(before: dict, after: dict) -> dict:
    """Return only changed keys as {key: {"from": x, "to": y}}.

    Keys present in one side but not the other are reported with the
    missing side as None. Identical dicts yield {}.
    """
    before_n = _normalize(before or {})
    after_n = _normalize(after or {})
    changes: dict[str, dict] = {}
    for key in set(before_n) | set(after_n):
        old = before_n.get(key)
        new = after_n.get(key)
        if old != new:
            changes[key] = {"from": old, "to": new}
    return changes


def snapshot(instance, fields: list[str]) -> dict:
    """Extract the given fields from a model instance as a plain dict."""
    return {f: _normalize(getattr(instance, f, None)) for f in fields}


# ---- DB writers ------------------------------------------------------------

def log_event(
    *,
    actor,
    action: str,
    entity_type: str,
    entity_id,
    changes: dict | None = None,
) -> AuditEvent:
    return AuditEvent.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes or {},
    )


def log_create(*, actor, instance, entity_type: str, fields: list[str] | None = None):
    payload = snapshot(instance, fields) if fields else {}
    return log_event(
        actor=actor,
        action=AuditEvent.Action.CREATE,
        entity_type=entity_type,
        entity_id=instance.pk,
        changes={"after": payload},
    )


def log_update(
    *,
    actor,
    instance,
    entity_type: str,
    before: dict,
    fields: list[str] | None = None,
):
    after = snapshot(instance, fields) if fields else {}
    changes = diff(before, after)
    if not changes:
        return None
    return log_event(
        actor=actor,
        action=AuditEvent.Action.UPDATE,
        entity_type=entity_type,
        entity_id=instance.pk,
        changes={"fields": changes},
    )


def log_delete(*, actor, instance, entity_type: str, fields: list[str] | None = None):
    payload = snapshot(instance, fields) if fields else {}
    return log_event(
        actor=actor,
        action=AuditEvent.Action.DELETE,
        entity_type=entity_type,
        entity_id=instance.pk,
        changes={"before": payload},
    )
