from django.urls import path

from app.views.notifications import (
    CreateNotificationView,
    GetNotificationsView,
    MarkReadNotificationView,
    NotificationPKAPI,
)

urlpatterns = [
    path("", CreateNotificationView.as_view(), name="create-notification"),
    path(
        "<str:notification_id>/",
        NotificationPKAPI.as_view(),
        name="notification-detail",
    ),
    path(
        "list/<str:receiver_id>/",
        GetNotificationsView.as_view(),
        name="get-notifications",
    ),
    path(
        "markread/<str:notification_id>/",
        MarkReadNotificationView.as_view(),
        name="mark-read-notification",
    ),
]
