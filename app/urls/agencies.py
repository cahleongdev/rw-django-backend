from django.urls import path

from app.views.agencies import AgencyAPI, AgencyPKAPI, AgencyUsersAPI, AgencyUserAPI, AgencyReportsAPI, AgencyBulkActionsAPI

urlpatterns = [
    path("", AgencyAPI.as_view(), name="agency-list-create"),
    path("<str:pk>/", AgencyPKAPI.as_view(), name="agency-detail"),
    path("<str:pk>/users/", AgencyUsersAPI.as_view(), name="agency-users"),
    path("<str:pk>/users/bulk/", AgencyBulkActionsAPI.as_view(), name="agency-users-bulk-actions"),
    path("<str:pk>/users/<str:user_id>/", AgencyUserAPI.as_view(), name="agency-user-detail"),
    path("<str:pk>/reports/", AgencyReportsAPI.as_view(), name="agency-reports"),
]
