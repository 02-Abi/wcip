from django.urls import path

from .views import (
    list_notifications,
    read_all_notifications,
    read_notification,
)

urlpatterns = [
    path("notifications/", list_notifications, name="notifications-list"),
    path(
        "notifications/read-all/",
        read_all_notifications,
        name="notifications-read-all",
    ),
    path(
        "notifications/<uuid:notification_id>/read/",
        read_notification,
        name="notification-read",
    ),
]
