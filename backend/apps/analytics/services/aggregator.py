"""Pure-Python analytics aggregators.

Every function here takes plain data (lists of dicts) and returns plain
data. No Django imports, no ORM — the views do the fetch. This keeps the
math unit-testable in isolation and fast.
"""

from __future__ import annotations

PROFICIENCY_ORDER = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
PROFICIENCY_RANK = {name: i + 1 for i, name in enumerate(PROFICIENCY_ORDER)}


def proficiency_distribution(employee_skills: list[dict]) -> dict:
    """Count how many employee-skill rows sit at each proficiency band.

    ``employee_skills`` items: {skill_id, skill_name, proficiency}.
    Returns {by_band: {...}, by_skill: [{skill_id, skill_name, counts, total}]}.
    """
    by_band = {band: 0 for band in PROFICIENCY_ORDER}
    per_skill: dict[str, dict] = {}

    for row in employee_skills:
        prof = row["proficiency"]
        if prof in by_band:
            by_band[prof] += 1
        entry = per_skill.setdefault(
            row["skill_id"],
            {
                "skill_id": row["skill_id"],
                "skill_name": row["skill_name"],
                "counts": {band: 0 for band in PROFICIENCY_ORDER},
                "total": 0,
            },
        )
        if prof in entry["counts"]:
            entry["counts"][prof] += 1
        entry["total"] += 1

    by_skill = sorted(per_skill.values(), key=lambda s: (-s["total"], s["skill_name"]))
    return {"by_band": by_band, "by_skill": by_skill}


def department_skill_coverage(
    departments: list[dict], employee_skills: list[dict]
) -> list[dict]:
    """For each department, coverage per skill = holders / headcount.

    ``departments`` items: {department_id, department_name, employee_ids: [str]}.
    ``employee_skills`` items: {employee_id, skill_id, skill_name, proficiency}.
    """
    holders: dict[str, dict[str, set]] = {}
    skill_names: dict[str, str] = {}
    for row in employee_skills:
        dept_ids = None
        holders.setdefault(row["skill_id"], {}).setdefault(row["employee_id"], None)
        skill_names[row["skill_id"]] = row["skill_name"]

    emp_to_dept: dict[str, str] = {}
    dept_meta: dict[str, dict] = {}
    for dept in departments:
        dept_meta[dept["department_id"]] = {
            "department_id": dept["department_id"],
            "department_name": dept["department_name"],
            "headcount": len(dept["employee_ids"]),
        }
        for emp_id in dept["employee_ids"]:
            emp_to_dept[emp_id] = dept["department_id"]

    # Count holders per (dept, skill)
    counts: dict[str, dict[str, int]] = {d: {} for d in dept_meta}
    for skill_id, emp_map in holders.items():
        for emp_id in emp_map:
            dept_id = emp_to_dept.get(emp_id)
            if dept_id is None:
                continue
            counts[dept_id][skill_id] = counts[dept_id].get(skill_id, 0) + 1

    result = []
    for dept_id, meta in dept_meta.items():
        per_skill = []
        for skill_id, n in counts[dept_id].items():
            headcount = meta["headcount"] or 1
            per_skill.append(
                {
                    "skill_id": skill_id,
                    "skill_name": skill_names.get(skill_id, skill_id),
                    "holders": n,
                    "coverage_pct": round((n / headcount) * 100, 2),
                }
            )
        per_skill.sort(key=lambda s: (-s["coverage_pct"], s["skill_name"]))
        result.append({**meta, "skills": per_skill})
    result.sort(key=lambda d: d["department_name"])
    return result


def top_gaps_across_projects(
    project_gap_reports: list[dict], limit: int = 10
) -> list[dict]:
    """Aggregate mandatory gaps from many employee_gap reports.

    ``project_gap_reports`` items: {project_id, project_name, gap: <employee_gap dict>}.
    Returns top skills by (missing count, total weight).
    """
    tally: dict[str, dict] = {}
    for report in project_gap_reports:
        gap = report["gap"]
        for item in gap.get("mandatory_gaps", []):
            key = item["skill_id"]
            entry = tally.setdefault(
                key,
                {
                    "skill_id": key,
                    "skill_name": item["skill_name"],
                    "gap_count": 0,
                    "total_weight": 0.0,
                    "projects": set(),
                },
            )
            entry["gap_count"] += 1
            entry["total_weight"] += float(item["weight"])
            entry["projects"].add(report["project_name"])

    out = []
    for entry in tally.values():
        out.append(
            {
                "skill_id": entry["skill_id"],
                "skill_name": entry["skill_name"],
                "gap_count": entry["gap_count"],
                "total_weight": round(entry["total_weight"], 2),
                "affected_projects": sorted(entry["projects"]),
            }
        )
    out.sort(key=lambda r: (-r["gap_count"], -r["total_weight"], r["skill_name"]))
    return out[:limit]


def department_capacity_summary(
    departments: list[dict], employees: list[dict], employee_skills: list[dict]
) -> list[dict]:
    """Headcount, avg skills/employee, avg experience, % verified skills.

    ``employees`` items: {employee_id, department_id, total_experience_years}.
    ``employee_skills`` items: {employee_id, is_verified}.
    """
    skills_per_emp: dict[str, int] = {}
    verified_per_emp: dict[str, int] = {}
    for row in employee_skills:
        skills_per_emp[row["employee_id"]] = skills_per_emp.get(row["employee_id"], 0) + 1
        if row.get("is_verified"):
            verified_per_emp[row["employee_id"]] = (
                verified_per_emp.get(row["employee_id"], 0) + 1
            )

    result = []
    for dept in departments:
        dept_id = dept["department_id"]
        members = [e for e in employees if e["department_id"] == dept_id]
        headcount = len(members)
        if headcount == 0:
            result.append(
                {
                    "department_id": dept_id,
                    "department_name": dept["department_name"],
                    "headcount": 0,
                    "avg_skills_per_employee": 0.0,
                    "avg_experience_years": 0.0,
                    "verified_skill_pct": 0.0,
                }
            )
            continue
        total_skills = sum(skills_per_emp.get(e["employee_id"], 0) for e in members)
        total_verified = sum(verified_per_emp.get(e["employee_id"], 0) for e in members)
        total_exp = sum(float(e.get("total_experience_years") or 0) for e in members)
        result.append(
            {
                "department_id": dept_id,
                "department_name": dept["department_name"],
                "headcount": headcount,
                "avg_skills_per_employee": round(total_skills / headcount, 2),
                "avg_experience_years": round(total_exp / headcount, 2),
                "verified_skill_pct": round((total_verified / total_skills) * 100, 2)
                if total_skills
                else 0.0,
            }
        )
    result.sort(key=lambda d: d["department_name"])
    return result
