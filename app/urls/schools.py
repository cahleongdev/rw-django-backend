from django.urls import path

from app.views.schools import (
    AgencyAdminSchoolAPI,
    SchoolAPI,
    SchoolPKAPI,
    SchoolSubmissionAPI,
    SchoolSubmissionDeleteAPI,
    SchoolBulkImportAPI,
)

urlpatterns = [
    path(
        "agency_admin/",
        AgencyAdminSchoolAPI.as_view(),
        name="agency-admin-school-list-create",
    ),
    path("", SchoolAPI.as_view(), name="school-list-create"),
    path("<str:pk>/", SchoolPKAPI.as_view(), name="school-detail"),
    path(
        "<str:pk>/reports/",
        SchoolSubmissionAPI.as_view(),
        name="school-report-list-create",
    ),
    path(
        "<str:pk>/report_delete/",
        SchoolSubmissionDeleteAPI.as_view(),
        name="school-report-list-create",
    ),
    path(
        "agency_admin/bulk",
        SchoolBulkImportAPI.as_view(),
        name="school-bulk-import",
    ),
]
