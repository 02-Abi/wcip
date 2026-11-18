"""Unit + API tests for notifications."""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Notification
from .services.notifier import (
    build_gap_alert,
    build_match_found,
    build_recommendation,
    mark_all_read,
    mark_read,
    notify_gap_alert,
    notify_match_found,
    notify_recommendation,
    send,
)

User = get_user_model()


def _gap_report(gaps=None):
    return {"mandatory_gaps": gaps or [], "optional_gaps": []}


class BuilderTests(TestCase):
    def test_gap_alert_builder(self):
        built = build_gap_alert(
            employee_name="Ada", project_name="Apollo", gap_count=3, top_skill="Python"
        )
        self.assertIn("Apollo", built["title"])
        self.assertIn("Ada", built["body"])
        self.assertIn("Python", built["body"])

    def test_gap_alert_builder_without_top_skill(self):
        built = build_gap_alert(
            employee_name="Ada", project_name="Apollo", gap_count=1, top_skill=None
        )
        self.assertTrue(built["body"].endswith("."))

    def test_recommendation_builder(self):
        built = build_recommendation(
            employee_name="Ada",
            top_skill="Python",
            action_type="upskill",
            effort_hours=40.0,
        )
        self.assertIn("Ada", built["title"])
        self.assertIn("upskill", built["body"])
        self.assertIn("Python", built["body"])

    def test_match_found_builder(self):
        built = build_match_found(
            project_name="Apollo", employee_name="Ada", score=87.5
        )
        self.assertIn("Apollo", built["title"])
        self.assertIn("87.5", built["body"])


class SendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")

    def test_send_creates_row(self):
        n = send(
            recipient=self.user,
            kind=Notification.Kind.SYSTEM,
            title="Hello",
            body="World",
            payload={"k": "v"},
        )
        self.assertEqual(n.recipient, self.user)
        self.assertEqual(n.kind, "SYSTEM")
        self.assertFalse(n.is_read)
        self.assertEqual(n.payload, {"k": "v"})

    def test_mark_read(self):
        n = send(recipient=self.user, kind=Notification.Kind.SYSTEM, title="T")
        mark_read(notification=n)
        n.refresh_from_db()
        self.assertTrue(n.is_read)
        self.assertIsNotNone(n.read_at)

    def test_mark_all_read(self):
        send(recipient=self.user, kind=Notification.Kind.SYSTEM, title="A")
        send(recipient=self.user, kind=Notification.Kind.SYSTEM, title="B")
        updated = mark_all_read(recipient=self.user)
        self.assertEqual(updated, 2)
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=True).count(), 2
        )


class DomainWrapperTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")

    def test_notify_gap_alert_no_gaps_returns_none(self):
        self.assertIsNone(
            notify_gap_alert(
                recipient=self.user,
                employee_name="Ada",
                project_name="Apollo",
                gap_report=_gap_report(),
            )
        )

    def test_notify_gap_alert_with_gaps_creates(self):
        gap = {"skill_name": "Python", "skill_id": "s1", "weight": 1.0, "is_mandatory": True}
        n = notify_gap_alert(
            recipient=self.user,
            employee_name="Ada",
            project_name="Apollo",
            gap_report=_gap_report([gap]),
        )
        self.assertIsNotNone(n)
        self.assertEqual(n.kind, "GAP_ALERT")
        self.assertEqual(n.payload["gap_count"], 1)

    def test_notify_recommendation_no_recs_returns_none(self):
        self.assertIsNone(
            notify_recommendation(
                recipient=self.user, employee_name="Ada", recommendations=[]
            )
        )

    def test_notify_recommendation_creates(self):
        rec = {
            "skill_id": "s1",
            "skill_name": "Python",
            "action_type": "upskill",
            "estimated_effort_hours": 20.0,
        }
        n = notify_recommendation(
            recipient=self.user, employee_name="Ada", recommendations=[rec]
        )
        self.assertEqual(n.kind, "RECOMMENDATION")
        self.assertEqual(n.payload["skill_id"], "s1")

    def test_notify_match_found_creates(self):
        n = notify_match_found(
            recipient=self.user,
            project_name="Apollo",
            employee_name="Ada",
            score=90.0,
        )
        self.assertEqual(n.kind, "MATCH_FOUND")


class NotificationApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")
        self.other = User.objects.create_user(username="other", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _mk(self, recipient=None, title="T", is_read=False):
        return Notification.objects.create(
            recipient=recipient or self.user,
            kind=Notification.Kind.SYSTEM,
            title=title,
            is_read=is_read,
        )

    def test_list_returns_only_mine(self):
        self._mk(title="mine")
        self._mk(recipient=self.other, title="theirs")
        resp = self.client.get("/api/notifications/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["notifications"][0]["title"], "mine")

    def test_list_unread_filter(self):
        self._mk(title="a", is_read=True)
        self._mk(title="b", is_read=False)
        resp = self.client.get("/api/notifications/?unread=1")
        body = resp.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["unread_count"], 1)

    def test_list_kind_filter(self):
        Notification.objects.create(
            recipient=self.user, kind=Notification.Kind.GAP_ALERT, title="g"
        )
        Notification.objects.create(
            recipient=self.user, kind=Notification.Kind.SYSTEM, title="s"
        )
        resp = self.client.get("/api/notifications/?kind=GAP_ALERT")
        self.assertEqual(resp.json()["count"], 1)

    def test_read_one(self):
        n = self._mk()
        resp = self.client.post(f"/api/notifications/{n.id}/read/")
        self.assertEqual(resp.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_read_other_users_notification_404(self):
        n = self._mk(recipient=self.other)
        resp = self.client.post(f"/api/notifications/{n.id}/read/")
        self.assertEqual(resp.status_code, 404)

    def test_read_all(self):
        self._mk()
        self._mk()
        resp = self.client.post("/api/notifications/read-all/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["marked_read"], 2)

    def test_requires_auth(self):
        anon = APIClient()
        self.assertIn(
            anon.get("/api/notifications/").status_code, (401, 403)
        )
