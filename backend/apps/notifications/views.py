"""User-facing notification inbox (self-scoped)."""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .services.notifier import mark_all_read, mark_read


def _serialize(n: Notification) -> dict:
    return {
        "id": str(n.id),
        "kind": n.kind,
        "title": n.title,
        "body": n.body,
        "payload": n.payload,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
        "read_at": n.read_at.isoformat() if n.read_at else None,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    qs = Notification.objects.filter(recipient=request.user)
    if request.query_params.get("unread") in {"1", "true", "True"}:
        qs = qs.filter(is_read=False)
    if kind := request.query_params.get("kind"):
        qs = qs.filter(kind=kind)

    try:
        limit = int(request.query_params.get("limit", 50))
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 200))

    items = list(qs[:limit])
    return Response(
        {
            "count": len(items),
            "unread_count": Notification.objects.filter(
                recipient=request.user, is_read=False
            ).count(),
            "notifications": [_serialize(n) for n in items],
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def read_notification(request, notification_id):
    n = get_object_or_404(
        Notification, pk=notification_id, recipient=request.user
    )
    mark_read(notification=n)
    return Response(_serialize(n))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def read_all_notifications(request):
    updated = mark_all_read(recipient=request.user)
    return Response({"marked_read": updated})
