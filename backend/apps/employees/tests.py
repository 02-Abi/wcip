"""Tests for the Employee and Department API."""
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Department, Employee


class EmployeeApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "tester", "tester@example.com", "tester-pass"
        )
        self.dept = Department.objects.create(name="Engineering", code="ENG")

    def _login(self):
        r = self.client.post(
            "/api/auth/token/",
            {"username": "tester", "password": "tester-pass"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.content)
        return r.data["access"]

    def test_create_and_list_employee(self):
        token = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload = {
            "employee_id": "E0001",
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "department": str(self.dept.id),
            "designation": "Engineer",
            "joining_date": "2020-01-15",
            "employment_status": "ACTIVE",
            "total_experience_years": "5.5",
        }
        r = self.client.post("/api/employees/", payload, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.data["employee_id"], "E0001")

        r = self.client.get("/api/employees/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["employee_id"], "E0001")

    def test_unauthorized_access_denied(self):
        r = self.client.get("/api/employees/")
        self.assertEqual(r.status_code, 401)