"""Unit + API tests for the skill-gap analyzer."""

import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.employees.models import Department, Employee
from apps.projects.models import Project, ProjectRequiredSkill
from apps.skills.models import EmployeeSkill, Skill, SkillCategory

from .services.analyzer import (
    classify_requirement,
    department_gap,
    employee_gap,
)

User = get_user_model()


def _req(skill_id="s1", name="Python", prof="INTERMEDIATE", years=2.0,
         mandatory=True, weight=1.0):
    return {
        "skill_id": skill_id,
        "skill_name": name,
        "minimum_proficiency": prof,
        "minimum_years": years,
        "is_mandatory": mandatory,
        "weight": weight,
    }


class ClassifyRequirementTests(TestCase):
    def test_missing_skill_is_marked_missing(self):
        item = classify_requirement(_req(), None)
        self.assertEqual(item.status, "missing")

    def test_exact_match_is_met(self):
        item = classify_requirement(
            _req(prof="INTERMEDIATE", years=2.0),
            {"proficiency": "INTERMEDIATE", "years_experience": 2.0},
        )
        self.assertEqual(item.status, "met")

    def test_higher_proficiency_but_short_years(self):
        item = classify_requirement(
            _req(prof="INTERMEDIATE", years=5.0),
            {"proficiency": "EXPERT", "years_experience": 1.0},
        )
        self.assertEqual(item.status, "insufficient_years")

    def test_lower_proficiency_wins_over_years(self):
        item = classify_requirement(
            _req(prof="ADVANCED", years=0.0),
            {"proficiency": "BEGINNER", "years_experience": 10.0},
        )
        self.assertEqual(item.status, "under_proficient")


class EmployeeGapTests(TestCase):
    def test_full_coverage_is_100(self):
        result = employee_gap(
            [_req(skill_id="a", prof="BEGINNER")],
            {"a": {"proficiency": "EXPERT", "years_experience": 5.0}},
        )
        self.assertEqual(result["coverage_pct"], 100.0)
        self.assertTrue(result["fully_qualified"])

    def test_empty_project_scores_zero_coverage(self):
        result = employee_gap([], {})
        self.assertEqual(result["coverage_pct"], 0.0)
        self.assertTrue(result["fully_qualified"])  # no mandatory gaps

    def test_mandatory_gap_blocks_fully_qualified(self):
        result = employee_gap(
            [_req(skill_id="a", prof="ADVANCED", mandatory=True)],
            {"a": {"proficiency": "BEGINNER", "years_experience": 1.0}},
        )
        self.assertFalse(result["fully_qualified"])
        self.assertEqual(len(result["mandatory_gaps"]), 1)

    def test_optional_gap_does_not_block(self):
        result = employee_gap(
            [_req(skill_id="a", prof="ADVANCED", mandatory=False)],
            {"a": {"proficiency": "BEGINNER", "years_experience": 1.0}},
        )
        self.assertTrue(result["fully_qualified"])
        self.assertEqual(len(result["optional_gaps"]), 1)

    def test_weighted_coverage(self):
        # requirement A weight 3 (met), B weight 1 (missing) -> 75%
        result = employee_gap(
            [
                _req(skill_id="a", prof="BEGINNER", weight=3.0),
                _req(skill_id="b", prof="BEGINNER", weight=1.0, mandatory=False),
            ],
            {"a": {"proficiency": "EXPERT", "years_experience": 5.0}},
        )
        self.assertEqual(result["coverage_pct"], 75.0)


class DepartmentGapTests(TestCase):
    def test_coverage_counts_meeting_employees(self):
        employees = [
            {"employee_id": "e1", "full_name": "A",
             "held_by_skill": {"a": {"proficiency": "EXPERT", "years_experience": 5}}},
            {"employee_id": "e2", "full_name": "B", "held_by_skill": {}},
        ]
        result = department_gap(
            [_req(skill_id="a", prof="INTERMEDIATE")], employees
        )
        self.assertEqual(result["per_skill"][0]["employees_meeting"], 1)
        self.assertEqual(result["per_skill"][0]["coverage_pct"], 50.0)
        self.assertEqual(result["overall_coverage_pct"], 50.0)

    def test_empty_department_no_division_error(self):
        result = department_gap([_req()], [])
        self.assertEqual(result["employee_count"], 0)
        self.assertEqual(result["overall_coverage_pct"], 0.0)


class SkillGapApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", password="pass12345"
        )
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
        self.skill = Skill.objects.create(category=cat, name="Python")
        EmployeeSkill.objects.create(
            employee=self.emp,
            skill=self.skill,
            proficiency="EXPERT",
            years_experience=Decimal("5.0"),
        )
        self.project = Project.objects.create(name="Apollo")
        ProjectRequiredSkill.objects.create(
            project=self.project,
            skill=self.skill,
            minimum_proficiency="INTERMEDIATE",
            minimum_years=Decimal("2.0"),
            is_mandatory=True,
            weight=Decimal("1.00"),
        )

    def test_employee_gap_requires_project_param(self):
        resp = self.client.get(f"/api/employees/{self.emp.id}/skill-gap/")
        self.assertEqual(resp.status_code, 400)

    def test_employee_gap_unknown_employee_404(self):
        resp = self.client.get(
            f"/api/employees/{uuid.uuid4()}/skill-gap/?project={self.project.id}"
        )
        self.assertEqual(resp.status_code, 404)

    def test_employee_gap_happy_path(self):
        resp = self.client.get(
            f"/api/employees/{self.emp.id}/skill-gap/?project={self.project.id}"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["coverage_pct"], 100.0)
        self.assertTrue(body["fully_qualified"])

    def test_department_gap_happy_path(self):
        resp = self.client.get(
            f"/api/departments/{self.dept.id}/skill-gap/?project={self.project.id}"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["employee_count"], 1)
        self.assertEqual(body["per_skill"][0]["coverage_pct"], 100.0)

    def test_endpoint_requires_auth(self):
        anon = APIClient()
        resp = anon.get(
            f"/api/employees/{self.emp.id}/skill-gap/?project={self.project.id}"
        )
        self.assertIn(resp.status_code, (401, 403))
