"""Pure-Python learning-recommendation engine.

Consumes the gap-report dicts produced by
``apps.gap_analysis.services.analyzer`` — no ORM, no Django imports.

Deterministic heuristic:
- Each proficiency band = HOURS_PER_LEVEL (20) hours of effort.
- Effort = bands_to_advance * HOURS_PER_LEVEL * weight
- Ranking: mandatory gaps first, then by effort descending
  (biggest need first), then by weight.
"""

from __future__ import annotations

PROFICIENCY_RANK = {
    "BEGINNER": 1,
    "INTERMEDIATE": 2,
    "ADVANCED": 3,
    "EXPERT": 4,
}
HOURS_PER_LEVEL = 20
ACTION_TYPE = {
    "missing": "learn_from_scratch",
    "under_proficient": "upskill",
    "insufficient_years": "gain_experience",
}


def _rank(value: str | None) -> int:
    return PROFICIENCY_RANK.get(value or "", 0)


def _bands_to_advance(current: str | None, target: str) -> int:
    gap = _rank(target) - _rank(current)
    return max(gap, 0)


def recommend_for_employee(
    gap_report: dict,
    catalog: dict[str, list[str]] | None = None,
) -> list[dict]:
    """Turn one employee's gap report into ranked learning actions.

    ``gap_report`` is the dict returned by ``employee_gap``.
    ``catalog`` optionally maps skill_id -> [related skill names] used
    to add a "practice alongside" hint. Purely cosmetic; safe to omit.
    """
    catalog = catalog or {}
    gaps = list(gap_report.get("mandatory_gaps", [])) + list(
        gap_report.get("optional_gaps", [])
    )

    recommendations: list[dict] = []
    for gap in gaps:
        status = gap["status"]
        if status == "missing":
            bands = _rank(gap["required_proficiency"])
        elif status == "under_proficient":
            bands = _bands_to_advance(
                gap.get("actual_proficiency"), gap["required_proficiency"]
            )
        else:  # insufficient_years
            bands = 1  # treat as one band of practical experience

        effort_hours = round(bands * HOURS_PER_LEVEL * float(gap["weight"]), 1)
        reason = _reason_for(status, gap)
        recommendations.append(
            {
                "priority": "mandatory" if gap["is_mandatory"] else "optional",
                "skill_id": gap["skill_id"],
                "skill_name": gap["skill_name"],
                "action_type": ACTION_TYPE.get(status, "upskill"),
                "reason": reason,
                "current_proficiency": gap.get("actual_proficiency"),
                "target_proficiency": gap["required_proficiency"],
                "estimated_effort_hours": effort_hours,
                "related_skills": catalog.get(gap["skill_id"], []),
            }
        )

    recommendations.sort(
        key=lambda r: (
            0 if r["priority"] == "mandatory" else 1,
            -r["estimated_effort_hours"],
            r["skill_name"],
        )
    )
    for idx, rec in enumerate(recommendations, start=1):
        rec["rank"] = idx
    return recommendations


def _reason_for(status: str, gap: dict) -> str:
    target = gap["required_proficiency"]
    if status == "missing":
        return f"No record of {gap['skill_name']}; build it up to {target}."
    if status == "under_proficient":
        return (
            f"Currently {gap.get('actual_proficiency')} in {gap['skill_name']}; "
            f"target is {target}."
        )
    return (
        f"Proficiency in {gap['skill_name']} is sufficient, but "
        f"{gap['required_years']} yrs are required vs "
        f"{gap.get('actual_years')} yrs recorded."
    )


def recommend_for_department(
    department_report: dict,
    catalog: dict[str, list[str]] | None = None,
) -> dict:
    """Roll up per-employee recommendations into a group-training view.

    Groups by skill, counts how many employees need it, and keeps the
    highest-priority row per skill. Returns
    ``{recommendation_count, group_actions, per_employee}``.
    """
    catalog = catalog or {}
    per_employee = []
    grouped: dict[str, dict] = {}

    for emp in department_report.get("per_employee", []):
        emp_recs = recommend_for_employee(emp, catalog)
        per_employee.append(
            {
                "employee_id": emp["employee_id"],
                "full_name": emp["full_name"],
                "recommendations": emp_recs,
            }
        )
        for rec in emp_recs:
            key = rec["skill_id"]
            if key not in grouped:
                grouped[key] = {**rec, "employee_count": 0, "employee_names": []}
            grouped[key]["employee_count"] += 1
            grouped[key]["employee_names"].append(emp["full_name"])

    group_actions = sorted(
        grouped.values(),
        key=lambda r: (
            0 if r["priority"] == "mandatory" else 1,
            -r["employee_count"],
            r["skill_name"],
        ),
    )
    for idx, action in enumerate(group_actions, start=1):
        action["rank"] = idx

    return {
        "recommendation_count": len(group_actions),
        "group_actions": group_actions,
        "per_employee": per_employee,
    }
