"""Notification helpers.

``send`` is the single DB writer. The ``notify_*`` functions are thin
domain wrappers — they build title/body/payload from existing engine
outputs (gap reports, recommendations, match results). Pure functions
where possible so they're unit-testable without touching the DB.
"""

from __future__ import annotations

from django.utils import timezone

from apps.notifications.models import Notification


# ---- pure builders ---------------------------------------------------------

def build_gap_alert(*, employee_name: str, project_name: str, gap_count: int, top_skill: str | None) -> dict:
    title = f"Skill gap detected: {project_name}"
    body = (
        f"{employee_name} has {gap_count} mandatory gap(s) for {project_name}"
        + (f", starting with {top_skill}." if top_skill else ".")
    )
    return {"title": title, "body": body}


def build_recommendation(*, employee_name: str, top_skill: str, action_type: str, effort_hours: float) -> dict:
    title = f"Learning recommendation for {employee_name}"
    body = (
        f"Top action: {action_type.replace('_', ' ')} in {top_skill} "
        f"(~{effort_hours:g}h estimated)."
    )
    return {"title": title, "body": body}


def build_match_found(*, project_name: str, employee_name: str, score: float) -> dict:
    title = f"Match found for {project_name}"
    body = f"{employee_name} scores {score:.1f} on this project."
    return {"title": title, "body": body}


# ---- DB writer -------------------------------------------------------------

def send(*, recipient, kind: str, title: str, body: str = "", payload: dict | None = None) -> Notification:
    return Notification.objects.create(
        recipient=recipient,
        kind=kind,
        title=title,
        body=body,
        payload=payload or {},
    )


def mark_read(*, notification: Notification) -> Notification:
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
    return notification


def mark_all_read(*, recipient) -> int:
    return Notification.objects.filter(recipient=recipient, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )


# ---- domain wrappers -------------------------------------------------------

def notify_gap_alert(*, recipient, employee_name: str, project_name: str, gap_report: dict) -> Notification | None:
    gaps = gap_report.get("mandatory_gaps", [])
    if not gaps:
        return None
    built = build_gap_alert(
        employee_name=employee_name,
        project_name=project_name,
        gap_count=len(gaps),
        top_skill=gaps[0]["skill_name"],
    )
    return send(
        recipient=recipient,
        kind=Notification.Kind.GAP_ALERT,
        title=built["title"],
        body=built["body"],
        payload={"gap_count": len(gaps), "project_name": project_name},
    )


def notify_recommendation(*, recipient, employee_name: str, recommendations: list[dict]) -> Notification | None:
    if not recommendations:
        return None
    top = recommendations[0]
    built = build_recommendation(
        employee_name=employee_name,
        top_skill=top["skill_name"],
        action_type=top["action_type"],
        effort_hours=float(top["estimated_effort_hours"]),
    )
    return send(
        recipient=recipient,
        kind=Notification.Kind.RECOMMENDATION,
        title=built["title"],
        body=built["body"],
        payload={"skill_id": top["skill_id"], "action_type": top["action_type"]},
    )


def notify_match_found(*, recipient, project_name: str, employee_name: str, score: float) -> Notification:
    built = build_match_found(
        project_name=project_name, employee_name=employee_name, score=score
    )
    return send(
        recipient=recipient,
        kind=Notification.Kind.MATCH_FOUND,
        title=built["title"],
        body=built["body"],
        payload={"project_name": project_name, "score": score},
    )
