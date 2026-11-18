"""Unit + API + integration tests for the audit log."""

import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.employees.models import Department, Employee

from .models import AuditEvent
from .services.logger import diff, log_create, log_delete, log_event, log_update

User = get_user_model()


# ---- unit: diff ------------------------------------------------------------

class DiffTests(TestCase):
    def test_identical_returns_empty(self):
        self.assertEqual(diff({"a": 1, "b": "x"}, {"a": 1, "b": "x"}), {})

    def test_detects_only_changed(self):
        result = diff({"a": 1, "b": "x"}, {"a": 2, "b": "x"})
        self.assertEqual(result, {"a": {"from": 1, "to": 2}})

    def test_added_and_removed_keys(self):
        result = diff({"a": 1}, {"b": 2})
        self.assertEqual(result["a"], {"from": 1, "to": None})
        self.assertEqual(result["b"], {"from": None, "to": 2})

    def test_decimal_normalized(self):
        result = diff({"x": Decimal("1.5")}, {"x": 1.5})
        self.assertEqual(result, {})


# ---- unit: log_event / helpers --------------------------------------------

class LoggerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")

    def test_log_event_creates_row(self):
        eid = uuid.uuid4()
        event = log_event(
            actor=self.user,
            action=AuditEvent.Action.CREATE,
            entity_type="thing",
            entity_id=eid,
            changes={"x": 1},
        )
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.entity_type, "thing")
        self.assertEqual(event.entity_id, eid)
        self.assertEqual(event.changes, {"x": 1})

    def test_log_event_null_actor_allowed(self):
        event = log_event(
            actor=None,
            action=AuditEvent.Action.DELETE,
            entity_type="thing",
            entity_id=uuid.uuid4(),
        )
        self.assertIsNone(event.actor)

    def test_anonymous_actor_becomes_null(self):
        from django.contrib.auth.models import AnonymousUser
        event = log_event(
            actor=AnonymousUser(),
            action=AuditEvent.Action.UPDATE,
            entity_type="thing",
            entity_id=uuid.uuid4(),
        )
        self.assertIsNone(event.actor)


# ---- API: read endpoint ----------------------------------------------------

class AuditReadApiTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="x", is_staff=True
        )
        self.normal = User.objects.create_user(username="norm", password="x")
        self.client = APIClient()

        self.entity_id = uuid.uuid4()
        log_event(
            actor=self.normal,
            action=AuditEvent.Action.CREATE,
            entity_type="employee",
            entity_id=self.entity_id,
            changes={"after": {"first_name": "Ada"}},
        )
        log_event(
            actor=self.normal,
            action=AuditEvent.Action.UPDATE,
            entity_type="employee",
            entity_id=self.entity_id,
            changes={"fields": {"first_name": {"from": "Ada", "to": "Ada L"}}},
        )
        log_event(
            actor=None,
            action=AuditEvent.Action.DELETE,
            entity_type="skill",
            entity_id=uuid.uuid4(),
        )

    def test_requires_staff(self):
        self.client.force_authenticate(user=self.normal)
        self.assertEqual(self.client.get("/api/audit/events/").status_code, 403)

    def test_requires_auth(self):
        anon = APIClient()
        self.assertIn(
            anon.get("/api/audit/events/").status_code, (401, 403)
        )

    def test_staff_gets_events(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get("/api/audit/events/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 3)

    def test_filter_by_entity_type(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get("/api/audit/events/?entity_type=employee")
        body = resp.json()
        self.assertEqual(body["count"], 2)
        self.assertTrue(all(e["entity_type"] == "employee" for e in body["events"]))

    def test_filter_by_action(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get("/api/audit/events/?action=DELETE")
        body = resp.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["events"][0]["action"], "DELETE")

    def test_filter_by_entity_id(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get(
            f"/api/audit/events/?entity_id={self.entity_id}"
        )
        self.assertEqual(resp.json()["count"], 2)

    def test_limit_capped(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get("/api/audit/events/?limit=9999")
        self.assertEqual(resp.json()["limit"], 500)


# ---- integration: employees viewsets write audit rows ---------------------

class EmployeeViewsetAuditIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.dept = Department.objects.create(name="Engineering", code="ENG")

    def _payload(self, **overrides):
        base = {
            "employee_id": "E100",
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "department": str(self.dept.id),
            "designation": "Engineer",
            "joining_date": "2024-01-01",
            "employment_status": "ACTIVE",
            "total_experience_years": "5.0",
        }
        base.update(overrides)
        return base

    def test_create_writes_audit_row(self):
        resp = self.client.post("/api/employees/", self._payload(), format="json")
        self.assertEqual(resp.status_code, 201)
        emp_id = resp.json()["id"]
        events = AuditEvent.objects.filter(
            entity_type="employee", entity_id=emp_id
        )
        self.assertEqual(events.count(), 1)
        event = events.first()
        self.assertEqual(event.action, "CREATE")
        self.assertEqual(event.actor, self.user)
        self.assertIn("after", event.changes)
        self.assertEqual(event.changes["after"]["first_name"], "Ada")

    def test_update_writes_diff(self):
        create = self.client.post("/api/employees/", self._payload(), format="json")
        emp_id = create.json()["id"]
        update = self.client.patch(
            f"/api/employees/{emp_id}/",
            {"designation": "Senior Engineer"},
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        event = AuditEvent.objects.get(
            entity_type="employee", entity_id=emp_id, action="UPDATE"
        )
        self.assertIn("designation", event.changes["fields"])
        self.assertEqual(
            event.changes["fields"]["designation"]["to"], "Senior Engineer"
        )

    def test_update_with_no_changes_writes_nothing(self):
        create = self.client.post("/api/employees/", self._payload(), format="json")
        emp_id = create.json()["id"]
        # Same designation - no diff -> no UPDATE event
        self.client.patch(
            f"/api/employees/{emp_id}/",
            {"designation": "Engineer"},
            format="json",
        )
        self.assertEqual(
            AuditEvent.objects.filter(
                entity_type="employee", entity_id=emp_id, action="UPDATE"
            ).count(),
            0,
        )

    def test_delete_writes_audit_row(self):
        create = self.client.post("/api/employees/", self._payload(), format="json")
        emp_id = create.json()["id"]
        delete = self.client.delete(f"/api/employees/{emp_id}/")
        self.assertEqual(delete.status_code, 204)
        event = AuditEvent.objects.get(
            entity_type="employee", entity_id=emp_id, action="DELETE"
        )
        self.assertEqual(event.changes["before"]["first_name"], "Ada")
