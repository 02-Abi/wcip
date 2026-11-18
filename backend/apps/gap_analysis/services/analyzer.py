"""Pure-Python skill-gap analyzer.

No ORM inside the scoring functions — they take plain data (requirement
dicts and employee-skill dicts) so they are unit-testable in isolation.
The thin adapter functions at the bottom do the one-time ORM fetch.

Proficiency is ordinal. Ranks:
    BEGINNER=1, INTERMEDIATE=2, ADVANCED=3, EXPERT=4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable

PROFICIENCY_RANK = {
    "BEGINNER": 1,
    "INTERMEDIATE": 2,
    "ADVANCED": 3,
    "EXPERT": 4,
}


def _rank(value: str) -> int:
    return PROFICIENCY_RANK.get(value, 0)


@dataclass
class GapItem:
    skill_id: str
    skill_name: str
    required_proficiency: str
    required_years: float
    actual_proficiency: str | None
    actual_years: float | None
    is_mandatory: bool
    weight: float
    status: str  # met | under_proficient | insufficient_years | missing

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "required_proficiency": self.required_proficiency,
            "required_years": self.required_years,
            "actual_proficiency": self.actual_proficiency,
            "actual_years": self.actual_years,
            "is_mandatory": self.is_mandatory,
            "weight": self.weight,
            "status": self.status,
        }


def classify_requirement(requirement: dict, held: dict | None) -> GapItem:
    """Classify a single requirement against what the employee holds.

    ``requirement`` keys: skill_id, skill_name, minimum_proficiency,
    minimum_years, is_mandatory, weight.
    ``held`` keys: proficiency, years_experience (or None if missing).
    """
    req_rank = _rank(requirement["minimum_proficiency"])
    req_years = float(requirement["minimum_years"])

    if held is None:
        status = "missing"
        actual_prof = None
        actual_years = None
    else:
        actual_prof = held["proficiency"]
        actual_years = float(held.get("years_experience") or 0)
        if _rank(actual_prof) < req_rank:
            status = "under_proficient"
        elif actual_years < req_years:
            status = "insufficient_years"
        else:
            status = "met"

    return GapItem(
        skill_id=str(requirement["skill_id"]),
        skill_name=requirement["skill_name"],
        required_proficiency=requirement["minimum_proficiency"],
        required_years=req_years,
        actual_proficiency=actual_prof,
        actual_years=actual_years,
        is_mandatory=bool(requirement["is_mandatory"]),
        weight=float(requirement["weight"]),
        status=status,
    )


def employee_gap(requirements: Iterable[dict], held_by_skill: dict[str, dict]) -> dict:
    """Compute one employee's gap against a list of requirements.

    ``held_by_skill`` maps skill_id -> {proficiency, years_experience}.
    """
    items = [
        classify_requirement(req, held_by_skill.get(str(req["skill_id"])))
        for req in requirements
    ]
    return _summarize(items, scope="employee")


def department_gap(requirements: Iterable[dict], employees: Iterable[dict]) -> dict:
    """Aggregate gap for a department.

    ``employees`` is a list of dicts with keys employee_id, full_name and
    held_by_skill (same shape as above). Each employee is scored
    individually, then rolled up per required skill.
    """
    req_list = list(requirements)
    emp_list = list(employees)

    per_employee = []
    for emp in emp_list:
        summary = employee_gap(req_list, emp["held_by_skill"])
        per_employee.append(
            {
                "employee_id": str(emp["employee_id"]),
                "full_name": emp["full_name"],
                **summary,
            }
        )

    # Per-skill coverage: how many employees meet each requirement.
    per_skill = []
    for req in req_list:
        met = 0
        for emp in emp_list:
            held = emp["held_by_skill"].get(str(req["skill_id"]))
            item = classify_requirement(req, held)
            if item.status == "met":
                met += 1
        total = len(emp_list)
        per_skill.append(
            {
                "skill_id": str(req["skill_id"]),
                "skill_name": req["skill_name"],
                "required_proficiency": req["minimum_proficiency"],
                "required_years": float(req["minimum_years"]),
                "is_mandatory": bool(req["is_mandatory"]),
                "employees_meeting": met,
                "employee_count": total,
                "coverage_pct": round((met / total) * 100, 2) if total else 0.0,
            }
        )

    mandatory = [s for s in per_skill if s["is_mandatory"]]
    overall = (
        round(sum(s["coverage_pct"] for s in mandatory) / len(mandatory), 2)
        if mandatory
        else 0.0
    )

    return {
        "scope": "department",
        "employee_count": len(emp_list),
        "requirement_count": len(req_list),
        "overall_coverage_pct": overall,
        "per_skill": per_skill,
        "per_employee": per_employee,
    }


def _summarize(items: list[GapItem], scope: str) -> dict:
    total_weight = sum(i.weight for i in items) or 1.0
    met_weight = sum(i.weight for i in items if i.status == "met")
    coverage = round((met_weight / total_weight) * 100, 2)

    mandatory_gaps = [
        i.to_dict() for i in items if i.is_mandatory and i.status != "met"
    ]
    optional_gaps = [
        i.to_dict() for i in items if not i.is_mandatory and i.status != "met"
    ]

    return {
        "scope": scope,
        "requirement_count": len(items),
        "coverage_pct": coverage,
        "fully_qualified": len(mandatory_gaps) == 0,
        "mandatory_gaps": mandatory_gaps,
        "optional_gaps": optional_gaps,
        "all_requirements": [i.to_dict() for i in items],
    }
