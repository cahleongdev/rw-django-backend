from django.urls import include, path

urlpatterns = [
    path("users/", include("app.urls.users")),
    path("auth/", include("app.urls.auth")),
    path("reports/", include("app.urls.reports")),
    path("schools/", include("app.urls.schools")),
    path("applications/", include("app.urls.applications")),
    path("school_applications/", include("app.urls.school_applications")),
    path("rubrics/", include("app.urls.rubrics")),
    path("frameworks/", include("app.urls.frameworks")),
    path("agencies/", include("app.urls.agencies")),
    path("submissions/", include("app.urls.submissions")),
    path("complaints/", include("app.urls.complaints")),
    path("files/", include("app.urls.files")),
    path("notifications/", include("app.urls.notifications")),
    path("messages/", include("app.urls.messages")),
    path("dashboards/", include("app.urls.dashboards")),
    path("room_messages/", include("app.urls.room_messages")),
    path("room/", include("app.urls.room")),
    path("documents/", include("app.urls.documents")),
    path("board_members/", include("app.urls.board_members")),
    path("transparency/", include("app.urls.transparency")),
]
