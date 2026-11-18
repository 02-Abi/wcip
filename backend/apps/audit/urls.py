from django.urls import path

from .views import audit_events

urlpatterns = [
    path("audit/events/", audit_events, name="audit-events"),
]
