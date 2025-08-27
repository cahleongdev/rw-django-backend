from django.urls import path

from app.views.dashboards import (
    DashboardsFilterValuesAPI,
    DashboardsGlanceAPI,
    DashboardsOutstandingReportsAPI,
    DashboardsOverdueReportsAPI,
)

urlpatterns = [
    path("glance/", DashboardsGlanceAPI.as_view(), name="glance-dashboard"),
    path(
        "overduereports/",
        DashboardsOverdueReportsAPI.as_view(),
        name="overdue-reports-dashboard",
    ),
    path(
        "outstandingreports/",
        DashboardsOutstandingReportsAPI.as_view(),
        name="outstanding-reports-dashboard",
    ),
    path(
        "filtervalues/",
        DashboardsFilterValuesAPI.as_view(),
        name="filter-values-dashboard",
    ),
]
