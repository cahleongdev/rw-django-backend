from django.urls import path

from app.views.complaints import AgencyAdminComplaintAPI, ComplaintAPI, ComplaintPKAPI

urlpatterns = [
    path(
        "agency_admin/",
        AgencyAdminComplaintAPI.as_view(),
        name="agency-admin-complaint-list-create",
    ),
    path("", ComplaintAPI.as_view(), name="complaint-list-create"),
    path("<str:pk>/", ComplaintPKAPI.as_view(), name="complaint-detail"),
]
