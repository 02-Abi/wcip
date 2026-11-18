"""Tests for the Projects app."""
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.skills.models import SkillCategory, Skill
from .models import Project, ProjectRequiredSkill


class ProjectsApiTests(APITestCase):
    def setUp(self):
        get_user_model().objects.create_user("pm", "pm@example.com", "pm-pass")
        r = self.client.post("/api/auth/token/", {"username": "pm", "password": "pm-pass"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        cat = SkillCategory.objects.create(name="Backend", description="")
        self.skill = Skill.objects.create(category=cat, name="Python")

    def test_create_project_and_requirement(self):
        r = self.client.post("/api/projects/", {
            "name": "Atlas", "description": "Internal platform",
            "status": "PLANNED", "priority": "HIGH",
            "start_date": "2026-01-01", "end_date": "2026-06-30", "headcount_needed": 3,
        }, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        project_id = r.data["id"]

        r = self.client.post("/api/project-required-skills/", {
            "project": project_id, "skill": str(self.skill.id),
            "minimum_proficiency": "ADVANCED", "minimum_years": "3.0",
            "is_mandatory": True, "weight": "2.5",
        }, format="json")
        self.assertEqual(r.status_code, 201, r.content)

        r = self.client.get(f"/api/project-required-skills/?project={project_id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)

    def test_project_date_validation_rejects_bad_range(self):
        r = self.client.post("/api/projects/", {
            "name": "Bad", "start_date": "2026-06-30", "end_date": "2026-01-01", "headcount_needed": 1,
        }, format="json")
        self.assertEqual(r.status_code, 400)

    def test_required_skill_weight_must_be_positive(self):
        r = self.client.post("/api/projects/", {"name": "P", "headcount_needed": 1}, format="json")
        project_id = r.data["id"]
        r = self.client.post("/api/project-required-skills/", {
            "project": project_id, "skill": str(self.skill.id), "weight": "0.00",
        }, format="json")
        self.assertEqual(r.status_code, 400)

    def test_unauthorized_project_access_denied(self):
        self.client.credentials()
        r = self.client.get("/api/projects/")
        self.assertEqual(r.status_code, 401)
