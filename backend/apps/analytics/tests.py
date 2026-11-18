"""Unit + API tests for the analytics aggregator and endpoints."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.employees.models import Department, Employee
from apps.projects.models import Project, ProjectRequiredSkill
from apps.skills.models import EmployeeSkill, Skill, SkillCategory

from .services.aggregator import (
    department_capacity_summary,
    department_skill_coverage,
    proficiency_distribution,
    top_gaps_across_projects,
)

User = get_user_model()


def _es(emp, skill, skill_name, prof, verified=False):
    return {
        "employee_id": emp,
        "skill_id": skill,
        "skill_name": skill_name,
        "proficiency": prof,
        "is_verified": verified,
    }


class ProficiencyDistributionTests(TestCase):
    def test_counts_by_band_and_skill(self):
        rows = [
            _es("e1", "s1", "Python", "BEGINNER"),
            _es("e2", "s1", "Python", "ADVANCED"),
            _es("e3", "s1", "Python", "ADVANCED"),
            _es("e1", "s2", "SQL", "INTERMEDIATE"),
        ]
        result = proficiency_distribution(rows)
        self.assertEqual(result["by_band"]["BEGINNER"], 1)
        self.assertEqual(result["by_band"]["ADVANCED"], 2)
        self.assertEqual(result["by_band"]["EXPERT"], 0)
        by_skill = {s["skill_name"]: s for s in result["by_skill"]}
        self.assertEqual(by_skill["Python"]["total"], 3)
        self.assertEqual(by_skill["Python"]["counts"]["ADVANCED"], 2)
        self.assertEqual(by_skill["SQL"]["total"], 1)

    def test_empty_input(self):
        result = proficiency_distribution([])
        self.assertEqual(result["by_band"], {b: 0 for b in [
            "BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"
        ]})
        self.assertEqual(result["by_skill"], [])

    def test_by_skill_sorted_by_total_desc(self):
        rows = [
            _es("e1", "s1", "A", "BEGINNER"),
            _es("e1", "s2", "B", "BEGINNER"),
            _es("e2", "s2", "B", "BEGINNER"),
        ]
        result = proficiency_distribution(rows)
        self.assertEqual([s["skill_name"] for s in result["by_skill"]], ["B", "A"])


class DepartmentSkillCoverageTests(TestCase):
    def test_coverage_math(self):
        depts = [
            {"department_id": "d1", "department_name": "Eng", "employee_ids": ["e1", "e2"]},
        ]
        rows = [
            _es("e1", "s1", "Python", "ADVANCED"),
            _es("e2", "s1", "Python", "BEGINNER"),
            _es("e1", "s2", "SQL", "ADVANCED"),
        ]
        result = department_skill_coverage(depts, rows)
        eng = result[0]
        self.assertEqual(eng["headcount"], 2)
        by_skill = {s["skill_name"]: s for s in eng["skills"]}
        self.assertEqual(by_skill["Python"]["holders"], 2)
        self.assertEqual(by_skill["Python"]["coverage_pct"], 100.0)
        self.assertEqual(by_skill["SQL"]["coverage_pct"], 50.0)

    def test_empty_department_zero_headcount(self):
        depts = [{"department_id": "d1", "department_name": "Empty", "employee_ids": []}]
        result = department_skill_coverage(depts, [])
        self.assertEqual(result[0]["headcount"], 0)
        self.assertEqual(result[0]["skills"], [])


class TopGapsTests(TestCase):
    def _gap(self, skill_id, name, weight=1.0):
        return {
            "skill_id": skill_id,
            "skill_name": name,
            "weight": weight,
            "is_mandatory": True,
            "status": "missing",
        }

    def test_aggregates_and_sorts(self):
        reports = [
            {"project_id": "p1", "project_name": "Apollo",
             "gap": {"mandatory_gaps": [self._gap("s1", "Python", 2.0)]}},
            {"project_id": "p2", "project_name": "Gemini",
             "gap": {"mandatory_gaps": [self._gap("s1", "Python", 2.0)]}},
            {"project_id": "p2", "project_name": "Gemini",
             "gap": {"mandatory_gaps": [self._gap("s2", "SQL", 1.0)]}},
        ]
        result = top_gaps_across_projects(reports)
        self.assertEqual(result[0]["skill_name"], "Python")
        self.assertEqual(result[0]["gap_count"], 2)
        self.assertEqual(result[0]["total_weight"], 4.0)
        self.assertEqual(result[0]["affected_projects"], ["Apollo", "Gemini"])
        self.assertEqual(result[1]["skill_name"], "SQL")

    def test_limit(self):
        reports = [
            {"project_id": "p1", "project_name": "P",
             "gap": {"mandatory_gaps": [self._gap(f"s{i}", f"S{i}")]}}
            for i in range(5)
        ]
        self.assertEqual(len(top_gaps_across_projects(reports, limit=2)), 2)

    def test_empty(self):
        self.assertEqual(top_gaps_across_projects([]), [])


class DepartmentCapacitySummaryTests(TestCase):
    def test_basic_summary(self):
        depts = [
            {"department_id": "d1", "department_name": "Eng"},
            {"department_id": "d2", "department_name": "Ops"},
        ]
        emps = [
            {"employee_id": "e1", "department_id": "d1", "total_experience_years": 5},
            {"employee_id": "e2", "department_id": "d1", "total_experience_years": 3},
        ]
        rows = [
            {"employee_id": "e1", "is_verified": True},
            {"employee_id": "e1", "is_verified": False},
            {"employee_id": "e2", "is_verified": True},
        ]
        result = department_capacity_summary(depts, emps, rows)
        eng = next(d for d in result if d["department_name"] == "Eng")
        ops = next(d for d in result if d["department_name"] == "Ops")
        self.assertEqual(eng["headcount"], 2)
        self.assertEqual(eng["avg_experience_years"], 4.0)
        self.assertEqual(eng["avg_skills_per_employee"], 1.5)
        # 2 verified out of 3 total skills = 66.67%
        self.assertEqual(eng["verified_skill_pct"], 66.67)
        self.assertEqual(ops["headcount"], 0)
        self.assertEqual(ops["avg_skills_per_employee"], 0.0)


class AnalyticsApiTests(TestCase):
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
            total_experience_years=Decimal("5.0"),
        )
        cat = SkillCategory.objects.create(name="Programming")
        self.skill = Skill.objects.create(category=cat, name="Python")
        EmployeeSkill.objects.create(
            employee=self.emp,
            skill=self.skill,
            proficiency="ADVANCED",
            years_experience=Decimal("3.0"),
            is_verified=True,
        )
        self.project = Project.objects.create(
            name="Apollo", status=Project.Status.ACTIVE
        )
        ProjectRequiredSkill.objects.create(
            project=self.project,
            skill=self.skill,
            minimum_proficiency="EXPERT",
            minimum_years=Decimal("5.0"),
            is_mandatory=True,
            weight=Decimal("1.00"),
        )

    def test_skills_analytics_returns_distribution(self):
        resp = self.client.get("/api/analytics/skills/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["by_band"]["ADVANCED"], 1)
        self.assertEqual(len(body["by_skill"]), 1)

    def test_skills_analytics_filter_by_department(self):
        resp = self.client.get(f"/api/analytics/skills/?department={self.dept.id}")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["by_band"]["ADVANCED"], 1)

    def test_skills_analytics_unknown_department_404(self):
        import uuid
        resp = self.client.get(f"/api/analytics/skills/?department={uuid.uuid4()}")
        self.assertEqual(resp.status_code, 404)

    def test_gaps_analytics_returns_top_gaps(self):
        resp = self.client.get("/api/analytics/gaps/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertGreaterEqual(len(body["top_gaps"]), 1)
        self.assertEqual(body["top_gaps"][0]["skill_name"], "Python")

    def test_departments_analytics_shape(self):
        resp = self.client.get("/api/analytics/departments/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body["departments"]), 1)
        dept = body["departments"][0]
        self.assertEqual(dept["headcount"], 1)
        self.assertEqual(dept["avg_skills_per_employee"], 1.0)

    def test_overview_shape(self):
        resp = self.client.get("/api/analytics/overview/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["headcount"], 1)
        self.assertEqual(body["department_count"], 1)
        self.assertEqual(body["active_project_count"], 1)
        self.assertEqual(body["proficiency_by_band"]["ADVANCED"], 1)

    def test_endpoints_require_auth(self):
        anon = APIClient()
        for url in [
            "/api/analytics/overview/",
            "/api/analytics/skills/",
            "/api/analytics/gaps/",
            "/api/analytics/departments/",
        ]:
            resp = anon.get(url)
            self.assertIn(resp.status_code, (401, 403), msg=url)
