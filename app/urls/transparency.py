from django.urls import path

from app.views.transparency import (
    TransparencyDetailsAPI,
    TransparencyFolderAPI,
    TransparencySubFolderAPI,
    TransparencyReportAPI,
    TransparencySchoolsAPI,
)

urlpatterns = [
    path("details/", TransparencyDetailsAPI.as_view(), name="transparency-details"),
    path(
        "details/<str:pk>/",
        TransparencyDetailsAPI.as_view(),
        name="transparency-details-detail",
    ),
    path("folders/", TransparencyFolderAPI.as_view(), name="transparency-folders"),
    path(
        "folders/<str:pk>/",
        TransparencyFolderAPI.as_view(),
        name="transparency-folder-detail",
    ),
    path(
        "sub-folders/",
        TransparencySubFolderAPI.as_view(),
        name="transparency-subfolders",
    ),
    path(
        "sub-folders/<str:pk>/",
        TransparencySubFolderAPI.as_view(),
        name="transparency-subfolder-detail",
    ),
    path("reports/", TransparencyReportAPI.as_view(), name="transparency-reports"),
    path(
        "schools/<str:pk>/",
        TransparencySchoolsAPI.as_view(),
        name="transparency-schools",
    ),
]
