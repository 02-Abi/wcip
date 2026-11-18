"""Unit + API tests for the matching engine."""
from decimal import Decimal
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.employees.models import Department, Employee
from apps.skills.models import SkillCategory, Skill, EmployeeSkill
from apps.projects.models import Project, ProjectRequiredSkill

from .services.matcher import (
    EmployeeData, EmployeeSkillData, SkillRequirement,
    score_employee_for_project, rank_matches,
)


def _req(name, prof="ADVANCED", years="2.0", mandatory=True, weight="1.00"):
    return SkillRequirement(
        skill_name=name, min_proficiency=prof, min_years=Decimal(years),
        is_mandatory=mandatory, weight=Decimal(weight),
    )


def _emp(name, skills):
    return EmployeeData(
        employee_id=name.upper(), full_name=name,
        skills=[EmployeeSkillData(skill_name=s[0], proficiency=s[1],
                                  years=Decimal(s[2]), is_verified=s[3]) for s in skills],
    )


class MatcherUnitTests(APITestCase):
    def test_full_match_scores_100(self):
        e = _emp("ada", [("Python", "ADVANCED", "3.0", False)])
        r = score_employee_for_project(e, [_req("Python", "ADVANCED", "3.0")])
        self.assertEqual(r["score"], 100.0)
        self.assertEqual(r["missing_mandatory_skills"], [])

    def test_missing_mandatory_zeroes_score(self):
        e = _emp("bob", [("Python", "EXPERT", "5.0", True)])
        r = score_employee_for_project(e, [_req("Go", "ADVANCED", "2.0")])
        self.assertEqual(r["score"], 0.0)
        self.assertEqual(r["missing_mandatory_skills"], ["Go"])

    def test_missing_optional_does_not_zero_score(self):
        e = _emp("cy", [("Python", "ADVANCED", "3.0", False)])
        r = score_employee_for_project(e, [
            _req("Python", "INTERMEDIATE", "1.0"),
            _req("Go", "BEGINNER", "1.0", mandatory=False, weight="0.50"),
        ])
        self.assertGreater(r["score"], 0.0)
        self.assertEqual(r["missing_optional_skills"], ["Go"])

    def test_ranking_sorts_by_score_desc(self):
        emps = [
            _emp("weak",   [("Python", "BEGINNER", "0.5", False)]),
            _emp("strong", [("Python", "EXPERT", "5.0", True)]),
        ]
        reqs = [_req("Python", "ADVANCED", "2.0")]
        ranked = rank_matches(emps, reqs)
        self.assertEqual(ranked[0]["employee_name"], "strong")
        self.assertEqual(ranked[-1]["employee_name"], "weak")


class MatchesApiTests(APITestCase):
    def setUp(self):
        get_user_model().objects.create_user("m", "m@example.com", "m-pass")
        r = self.client.post("/api/auth/token/", {"username": "m", "password": "m-pass"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

        self.cat = SkillCategory.objects.create(name="Backend", description="")
        self.py = Skill.objects.create(category=self.cat, name="Python")
        self.dept = Department.objects.create(name="Eng", code="ENG")

        self.proj = Project.objects.create(name="Atlas", headcount_needed=1)
        ProjectRequiredSkill.objects.create(
            project=self.proj, skill=self.py,
            minimum_proficiency="ADVANCED", minimum_years=Decimal("2.0"),
            is_mandatory=True, weight=Decimal("1.0"),
        )

        e1 = Employee.objects.create(
            employee_id="E1", first_name="Ada", last_name="Lovelace",
            email="ada@example.com", department=self.dept, designation="Eng",
            joining_date="2020-01-01", employment_status="ACTIVE",
            total_experience_years=5,
        )
        EmployeeSkill.objects.create(
            employee=e1, skill=self.py, proficiency="ADVANCED",
            years_experience=Decimal("3.0"), is_verified=True,
        )
        e2 = Employee.objects.create(
            employee_id="E2", first_name="Bob", last_name="Weak",
            email="bob@example.com", department=self.dept, designation="Eng",
            joining_date="2020-01-01", employment_status="ACTIVE",
            total_experience_years=1,
        )
        EmployeeSkill.objects.create(
            employee=e2, skill=self.py, proficiency="BEGINNER",
            years_experience=Decimal("0.5"), is_verified=False,
        )

    def test_matches_endpoint_returns_ranked(self):
        r = self.client.get(f"/api/projects/{self.proj.id}/matches/")
        self.assertEqual(r.status_code, 200, r.content)
        matches = r.data["matches"]
        self.assertGreaterEqual(len(matches), 2)
        self.assertEqual(matches[0]["employee_id"], "E1")
        self.assertGreater(matches[0]["score"], matches[1]["score"])

    def test_matches_endpoint_unauthorized(self):
        self.client.credentials()
        r = self.client.get(f"/api/projects/{self.proj.id}/matches/")
        self.assertEqual(r.status_code, 401)
