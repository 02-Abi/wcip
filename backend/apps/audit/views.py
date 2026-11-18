"""Read-only audit-event API (staff only)."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import AuditEvent


def _serialize(event: AuditEvent) -> dict:
    return {
        "id": str(event.id),
        "actor_id": str(event.actor_id) if event.actor_id else None,
        "action": event.action,
        "entity_type": event.entity_type,
        "entity_id": str(event.entity_id),
        "changes": event.changes,
        "created_at": event.created_at.isoformat(),
    }


@api_view(["GET"])
@permission_classes([IsAdminUser])
def audit_events(request):
    qs = AuditEvent.objects.select_related("actor").all()

    if entity_type := request.query_params.get("entity_type"):
        qs = qs.filter(entity_type=entity_type)
    if entity_id := request.query_params.get("entity_id"):
        qs = qs.filter(entity_id=entity_id)
    if action := request.query_params.get("action"):
        qs = qs.filter(action=action)
    if actor_id := request.query_params.get("actor_id"):
        qs = qs.filter(actor_id=actor_id)

    try:
        limit = int(request.query_params.get("limit", 50))
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 500))

    events = list(qs[:limit])
    return Response(
        {
            "count": len(events),
            "limit": limit,
            "events": [_serialize(e) for e in events],
        }
    )
