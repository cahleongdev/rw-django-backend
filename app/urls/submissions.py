from django.urls import path

from app.views.submissions import (
    SubmissionAPI,
    SubmissionFilterAPI,
    SubmissionMessageAPI,
    SubmissionPKAPI,
    SubmissionsBySchoolAPI,
    SubmissionsAdminByReportAPI,
    SubmissionsAdminBySchoolAPI,
    SubmissionAssignedUserAPI,
    SubmissionDownloadAPI,
    SchoolSubmissionDownloadAPI,
    ReportSubmissionDownloadAPI,
    SubmissionAssignEvaluatorAPI,
)

urlpatterns = [
    path(
        "agency_admin/by_report/",
        SubmissionsAdminByReportAPI.as_view(),
        name="submission-list-by-report",
    ),
    path(
        "assign_evaluator/",
        SubmissionAssignEvaluatorAPI.as_view(),
        name="submission-assign-evaluator",
    ),
    path(
        "assigned_user/",
        SubmissionAssignedUserAPI.as_view(),
        name="submission-assigned-user",
    ),
    path(
        "agency_admin/by_school/",
        SubmissionsAdminBySchoolAPI.as_view(),
        name="submission-list-by-school",
    ),
    path(
        "filter/<str:type>/<str:pk>/",
        SubmissionFilterAPI.as_view(),
        name="submission-filter",
    ),
    path(
        "by_school/<str:school_pk>/",
        SubmissionsBySchoolAPI.as_view(),
        name="submission-school-list",
    ),
    path("", SubmissionAPI.as_view(), name="submission-list-create"),
    path("<str:pk>/", SubmissionPKAPI.as_view(), name="submission-detail"),
    path(
        "download/<str:pk>/",
        SubmissionDownloadAPI.as_view(),
        name="submission-download",
    ),
    path(
        "download/school/<str:pk>/",
        SchoolSubmissionDownloadAPI.as_view(),
        name="school-submission-download",
    ),
    path(
        "download/report/<str:pk>/",
        ReportSubmissionDownloadAPI.as_view(),
        name="report-submission-download",
    ),
    path(
        "messages/<str:submission_pk>/",
        SubmissionMessageAPI.as_view(),
        name="submission-message-list",
    ),
]
