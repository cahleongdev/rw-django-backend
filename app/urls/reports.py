from django.urls import path

from app.views.report_activities import ReportActivityAPI, ReportActivityDetailAPI
from app.views.reports import (
    AgencyAdminReportAPI,
    ReportAPI,
    ReportBulkDeleteAPI,
    ReportCategoryAPI,
    ReportDuplicateAPI,
    ReportPKAPI,
    ReportSchoolAssignAPI,
)

urlpatterns = [
    # More specific routes first
    path(
        "activities/<str:activity_id>/",
        ReportActivityDetailAPI.as_view(),
        name="report-activity-detail",
    ),
    path("activities/", ReportActivityAPI.as_view(), name="report-activities"),
    path(
        "categories/report_category/",
        ReportCategoryAPI.as_view(),
        name="report-category-list-create",
    ),
    path("bulk/delete/", ReportBulkDeleteAPI.as_view(), name="report-bulk-delete"),
    path(
        "schools/assign/", ReportSchoolAssignAPI.as_view(), name="report-school-assign"
    ),
    path(
        "agency_admin/",
        AgencyAdminReportAPI.as_view(),
        name="agency-admin-report-list-create",
    ),
    # General report routes last
    path("<str:pk>/", ReportPKAPI.as_view(), name="report-detail"),
    path("", ReportAPI.as_view(), name="report-list-create"),
    path("duplicate/<str:pk>/", ReportDuplicateAPI.as_view(), name="report-duplicate"),
]
