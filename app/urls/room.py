from django.urls import path

from app.views.rooms import (
    AnnouncementAPI,
    AnnouncementCategoryAPI,
    RoomAPI,
    RoomArchiveAPI,
    RoomDetailAPI,
)

urlpatterns = [
    path("", RoomAPI.as_view(), name="room-list-create"),
    path("announcement/", AnnouncementAPI.as_view(), name="announcement-list-create"),
    path(
        "announcement/categories/",
        AnnouncementCategoryAPI.as_view(),
        name="announcement-category-list-create",
    ),
    path("<str:room_id>/", RoomDetailAPI.as_view(), name="room-detail"),
    path("<str:room_id>/archive/", RoomArchiveAPI.as_view(), name="room-archive"),
]
