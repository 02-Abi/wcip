from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import SkillCategory, Skill
from apps.employees.models import Department, Employee


class SkillsApiTests(APITestCase):
    def setUp(self):
        get_user_model().objects.create_user("skt", "skt@example.com", "pw")
        r = self.client.post("/api/auth/token/", {"username": "skt", "password": "pw"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

    def test_create_category_and_skill(self):
        r = self.client.post("/api/skill-categories/", {"name": "Backend", "description": "BE"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        cat_id = r.data["id"]
        r = self.client.post("/api/skills/", {"category": cat_id, "name": "Python"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        r = self.client.get("/api/skills/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)

    def test_link_employee_to_skill(self):
        cat = SkillCategory.objects.create(name="Backend", description="")
        sk = Skill.objects.create(category=cat, name="Python")
        dept = Department.objects.create(name="Engineering", code="ENG")
        emp = Employee.objects.create(
            employee_id="E0001", first_name="Ada", last_name="Lovelace",
            email="ada@example.com", department=dept, designation="Engineer",
            joining_date="2020-01-15", employment_status="ACTIVE", total_experience_years=5,
        )
        r = self.client.post("/api/employee-skills/",
            {"employee": str(emp.id), "skill": str(sk.id), "proficiency": "ADVANCED", "years_experience": "4.0"},
            format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.data["proficiency"], "ADVANCED")
