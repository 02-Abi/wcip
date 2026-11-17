"""Health-check endpoint used by load balancers, CI, and uptime monitoring.

Contract:
    GET /api/health/  → 200 {"status": "ok",       "database": "ok",    ...}
    GET /api/health/  → 503 {"status": "degraded", "database": "error", ...}

Never raises an exception to the client; failures are reported as JSON with 503.
"""
from datetime import datetime, timezone
import django
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    payload = {
        "status": "ok",
        "database": "ok",
        "django": django.get_version(),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    http_status = 200
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
    except Exception as exc:  # noqa: BLE001 — we surface the message to operators
        payload["status"] = "degraded"
        payload["database"] = "error"
        payload["error"] = f"{type(exc).__name__}: {exc}"
        http_status = 503
    return Response(payload, status=http_status)