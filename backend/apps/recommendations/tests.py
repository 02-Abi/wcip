"""Unit + API tests for the learning-recommendation engine."""

import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.employees.models import Department, Employee
from apps.projects.models import Project, ProjectRequiredSkill
from apps.skills.models import EmployeeSkill, Skill, SkillCategory

from .services.engine import (
    recommend_for_department,
    recommend_for_employee,
)

User = get_user_model()


def _gap(**overrides):
    base = {
        "skill_id": "s1",
        "skill_name": "Python",
        "required_proficiency": "INTERMEDIATE",
        "required_years": 2.0,
        "actual_proficiency": "BEGINNER",
        "actual_years": 0.5,
        "is_mandatory": True,
        "weight": 1.0,
        "status": "under_proficient",
    }
    base.update(overrides)
    return base


def _report(mandatory=None, optional=None):
    return {
        "mandatory_gaps": mandatory or [],
        "optional_gaps": optional or [],
        "coverage_pct": 50.0,
        "fully_qualified": False,
    }


class EmployeeRecommendationTests(TestCase):
    def test_missing_skill_produces_learn_from_scratch(self):
        recs = recommend_for_employee(
            _report(mandatory=[_gap(status="missing", actual_proficiency=None)])
        )
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["action_type"], "learn_from_scratch")
        self.assertEqual(recs[0]["priority"], "mandatory")
        self.assertEqual(recs[0]["rank"], 1)

    def test_under_proficient_produces_upskill(self):
        recs = recommend_for_employee(_report(mandatory=[_gap()]))
        self.assertEqual(recs[0]["action_type"], "upskill")
        # 1 band (BEGINNER->INTERMEDIATE) * 20 * weight 1.0 = 20.0
        self.assertEqual(recs[0]["estimated_effort_hours"], 20.0)

    def test_insufficient_years_produces_gain_experience(self):
        recs = recommend_for_employee(
            _report(
                mandatory=[
                    _gap(
                        status="insufficient_years",
                        actual_proficiency="EXPERT",
                        actual_years=1.0,
                    )
                ]
            )
        )
        self.assertEqual(recs[0]["action_type"], "gain_experience")

    def test_mandatory_sorted_before_optional(self):
        recs = recommend_for_employee(
            _report(
                mandatory=[_gap(skill_id="m", skill_name="Mand", weight=1.0)],
                optional=[
                    _gap(
                        skill_id="o",
                        skill_name="Opt",
                        is_mandatory=False,
                        weight=5.0,
                    )
                ],
            )
        )
        self.assertEqual(recs[0]["skill_id"], "m")
        self.assertEqual(recs[1]["skill_id"], "o")

    def test_empty_report_returns_no_recommendations(self):
        self.assertEqual(recommend_for_employee(_report()), [])

    def test_catalog_attaches_related_skills(self):
        recs = recommend_for_employee(
            _report(mandatory=[_gap(skill_id="s1")]),
            catalog={"s1": ["Django", "Flask"]},
        )
        self.assertEqual(recs[0]["related_skills"], ["Django", "Flask"])

    def test_ranks_are_sequential(self):
        recs = recommend_for_employee(
            _report(
                mandatory=[
                    _gap(skill_id="a", skill_name="A", weight=1.0),
                    _gap(skill_id="b", skill_name="B", weight=3.0),
                ]
            )
        )
        self.assertEqual([r["rank"] for r in recs], [1, 2])
        # higher weight -> higher effort -> ranked first
        self.assertEqual(recs[0]["skill_id"], "b")


class DepartmentRecommendationTests(TestCase):
    def _emp(self, eid, name, gaps):
        return {
            "employee_id": eid,
            "full_name": name,
            "mandatory_gaps": gaps,
            "optional_gaps": [],
            "coverage_pct": 0.0,
            "fully_qualified": False,
        }

    def test_groups_shared_skill_across_employees(self):
        shared = _gap(skill_id="shared", skill_name="SQL")
        report = {
            "per_employee": [
                self._emp("e1", "Ada", [shared]),
                self._emp("e2", "Bob", [shared]),
            ]
        }
        result = recommend_for_department(report)
        self.assertEqual(result["recommendation_count"], 1)
        action = result["group_actions"][0]
        self.assertEqual(action["employee_count"], 2)
        self.assertIn("Ada", action["employee_names"])
        self.assertIn("Bob", action["employee_names"])

    def test_empty_department(self):
        result = recommend_for_department({"per_employee": []})
        self.assertEqual(result["recommendation_count"], 0)
        self.assertEqual(result["group_actions"], [])
        self.assertEqual(result["per_employee"], [])


class RecommendationApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.dept = Department.objects.create(name="Engineering", code="ENG")
        self.emp = Employee.objects.create(
            employee_id="E001",
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            department=self.dept,
            designation="Engineer",
            joining_date="2024-01-01",
        )
        cat = SkillCategory.objects.create(name="Programming")
        self.py = Skill.objects.create(category=cat, name="Python")
        self.dj = Skill.objects.create(category=cat, name="Django")
        EmployeeSkill.objects.create(
            employee=self.emp,
            skill=self.py,
            proficiency="BEGINNER",
            years_experience=Decimal("0.5"),
        )
        self.project = Project.objects.create(name="Apollo")
        ProjectRequiredSkill.objects.create(
            project=self.project,
            skill=self.py,
            minimum_proficiency="ADVANCED",
            minimum_years=Decimal("2.0"),
            is_mandatory=True,
            weight=Decimal("1.00"),
        )
        ProjectRequiredSkill.objects.create(
            project=self.project,
            skill=self.dj,
            minimum_proficiency="INTERMEDIATE",
            minimum_years=Decimal("0.0"),
            is_mandatory=False,
            weight=Decimal("1.00"),
        )

    def test_employee_recommendations_requires_project(self):
        resp = self.client.get(f"/api/employees/{self.emp.id}/recommendations/")
        self.assertEqual(resp.status_code, 400)

    def test_employee_recommendations_unknown_employee(self):
        resp = self.client.get(
            f"/api/employees/{uuid.uuid4()}/recommendations/?project={self.project.id}"
        )
        self.assertEqual(resp.status_code, 404)

    def test_employee_recommendations_happy_path(self):
        resp = self.client.get(
            f"/api/employees/{self.emp.id}/recommendations/?project={self.project.id}"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["recommendation_count"], 2)
        # Python under-proficient is mandatory -> rank 1
        self.assertEqual(body["recommendations"][0]["skill_name"], "Python")
        self.assertEqual(body["recommendations"][0]["action_type"], "upskill")
        # related skill (Django) should be attached
        self.assertIn("Django", body["recommendations"][0]["related_skills"])

    def test_department_recommendations_happy_path(self):
        resp = self.client.get(
            f"/api/departments/{self.dept.id}/recommendations/?project={self.project.id}"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body["per_employee"]), 1)
        self.assertGreaterEqual(body["recommendation_count"], 1)

    def test_endpoint_requires_auth(self):
        anon = APIClient()
        resp = anon.get(
            f"/api/employees/{self.emp.id}/recommendations/?project={self.project.id}"
        )
        self.assertIn(resp.status_code, (401, 403))

