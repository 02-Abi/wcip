"""Pure-Python employee matching engine.

No Django ORM calls inside `score_employee_for_project` — it receives
plain data. `find_matches_for_project` is the thin DB-facing wrapper.

Formula (documented in the project README):

    score = 0
    for each required skill R in project.required_skills:
        es = employee's skill entry for R.skill
        if es is None:
            if R.is_mandatory: return (0, missing_mandatory=[R.skill.name])
            else: missing_optional.append(...); continue
        proficiency_factor = min(rank(es.proficiency) / rank(R.min_proficiency), 1.0)
        experience_factor  = min(es.years_experience / max(R.minimum_years, 0.1), 1.0)
        verified_bonus     = 0.05 if es.is_verified else 0.0
        skill_score        = R.weight * (0.6 * proficiency_factor + 0.4 * experience_factor + verified_bonus)
        score += skill_score

    total_weight = sum(R.weight for R in project.required_skills)
    score_percent = 100 * score / total_weight    # capped at 100
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


@dataclass
class SkillRequirement:
    skill_name: str
    min_proficiency: str
    min_years: Decimal
    is_mandatory: bool
    weight: Decimal


@dataclass
class EmployeeSkillData:
    skill_name: str
    proficiency: str
    years: Decimal
    is_verified: bool


@dataclass
class EmployeeData:
    employee_id: str
    full_name: str
    skills: list[EmployeeSkillData] = field(default_factory=list)


def _rank(proficiency: str) -> int:
    return PROFICIENCY_RANK.get(proficiency, 0)


def _safe_ratio(numerator: Decimal, denominator: Decimal) -> float:
    denom = float(denominator) if denominator else 0.0
    if denom <= 0:
        return 1.0 if float(numerator) > 0 else 0.0
    return min(float(numerator) / denom, 1.0)


def score_employee_for_project(
    employee: EmployeeData,
    requirements: list[SkillRequirement],
) -> dict:
    """Return a dict describing the match; `score` is 0..100."""
    if not requirements:
        return {
            "employee_id": employee.employee_id,
            "employee_name": employee.full_name,
            "score": 0.0,
            "matched_skills": [],
            "missing_mandatory_skills": [],
            "missing_optional_skills": [],
            "explanation": "Project has no required skills defined.",
        }

    by_name = {s.skill_name: s for s in employee.skills}

    total_weight = sum(float(r.weight) for r in requirements) or 1.0
    raw_score = 0.0
    matched = []
    missing_mandatory = []
    missing_optional = []

    for req in requirements:
        es = by_name.get(req.skill_name)
        if es is None:
            if req.is_mandatory:
                missing_mandatory.append(req.skill_name)
            else:
                missing_optional.append(req.skill_name)
            continue

        prof_factor = min(
            _rank(es.proficiency) / max(_rank(req.min_proficiency), 1), 1.0
        )
        exp_factor = _safe_ratio(es.years, req.min_years if req.min_years else Decimal("0.1"))
        verified_bonus = 0.05 if es.is_verified else 0.0
        raw_score += float(req.weight) * (0.6 * prof_factor + 0.4 * exp_factor + verified_bonus)
        matched.append({
            "skill": req.skill_name,
            "proficiency": es.proficiency,
            "years": float(es.years),
            "is_verified": es.is_verified,
        })

    if missing_mandatory:
        return {
            "employee_id": employee.employee_id,
            "employee_name": employee.full_name,
            "score": 0.0,
            "matched_skills": matched,
            "missing_mandatory_skills": missing_mandatory,
            "missing_optional_skills": missing_optional,
            "explanation": (
                "Cannot be considered: missing mandatory skill(s) "
                + ", ".join(missing_mandatory)
            ),
        }

    score_percent = min(100.0, 100.0 * raw_score / total_weight)
    if not missing_optional:
        explanation = (
            f"Matched all {len(requirements)} requirement(s); "
            f"score {score_percent:.1f}."
        )
    else:
        explanation = (
            f"Matched {len(matched)}/{len(requirements)} requirement(s); "
            f"missing optional: {', '.join(missing_optional)}."
        )

    return {
        "employee_id": employee.employee_id,
        "employee_name": employee.full_name,
        "score": round(score_percent, 2),
        "matched_skills": matched,
        "missing_mandatory_skills": [],
        "missing_optional_skills": missing_optional,
        "explanation": explanation,
    }


def rank_matches(employees: Iterable[EmployeeData],
                 requirements: list[SkillRequirement],
                 top_n: int | None = None) -> list[dict]:
    results = [score_employee_for_project(e, requirements) for e in employees]
    results.sort(key=lambda r: (-r["score"], r["employee_name"]))
    if top_n is not None:
        results = results[:top_n]
    return results


def find_matches_for_project(project, employees_qs, top_n: int | None = None) -> list[dict]:
    """DB-facing wrapper: project -> required skills -> rank employees."""
    requirements = [
        SkillRequirement(
            skill_name=prs.skill.name,
            min_proficiency=prs.minimum_proficiency,
            min_years=prs.minimum_years,
            is_mandatory=prs.is_mandatory,
            weight=prs.weight,
        )
        for prs in project.required_skills.select_related("skill").all()
    ]

    employee_datas = []
    for emp in employees_qs.prefetch_related("skills__skill"):
        employee_datas.append(EmployeeData(
            employee_id=emp.employee_id,
            full_name=f"{emp.first_name} {emp.last_name}".strip(),
            skills=[
                EmployeeSkillData(
                    skill_name=es.skill.name,
                    proficiency=es.proficiency,
                    years=es.years_experience,
                    is_verified=es.is_verified,
                )
                for es in emp.skills.all()
            ],
        ))

    return rank_matches(employee_datas, requirements, top_n=top_n)
