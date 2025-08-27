from django.urls import path

from app.views.room_messages import MarkMessageAsReadAPI, RoomMessagesAPI

urlpatterns = [
    path("<str:room_id>/", RoomMessagesAPI.as_view(), name="room-message-list-create"),
    path(
        "<str:room_id>/mark-as-read/<str:message_id>/",
        MarkMessageAsReadAPI.as_view(),
        name="mark-message-as-read",
    ),
]
