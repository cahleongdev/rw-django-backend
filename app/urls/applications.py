from django.urls import path

from app.views.applications import (
    AgencyAdminApplicationAPI,
    ApplicationAPI,
    ApplicationPKAPI,
    ApplicationQuestionAPI,
    ApplicationQuestionPKAPI,
    ApplicationSectionAPI,
    ApplicationSectionPKAPI,
    ApplicationSubSectionAPI,
    ApplicationSubSectionPKAPI,
)

urlpatterns = [
    path(
        "sub_sections/<str:section_pk>/",
        ApplicationSubSectionAPI.as_view(),
        name="application-sub-section-list",
    ),
    path(
        "sub_section_detail/<str:pk>/",
        ApplicationSubSectionPKAPI.as_view(),
        name="application-sub-section-detail",
    ),
    path(
        "questions/<str:sub_section_pk>/",
        ApplicationQuestionAPI.as_view(),
        name="application-question-list",
    ),
    path(
        "question_detail/<str:pk>/",
        ApplicationQuestionPKAPI.as_view(),
        name="application-question-detail",
    ),
    path("sections/", ApplicationSectionAPI.as_view(), name="application-section"),
    path(
        "sections/<str:section_pk>/",
        ApplicationSectionPKAPI.as_view(),
        name="application-section-detail",
    ),
    path(
        "agency_admin/",
        AgencyAdminApplicationAPI.as_view(),
        name="application-list-create",
    ),
    path("", ApplicationAPI.as_view(), name="application-list-create"),
    path("<str:pk>/", ApplicationPKAPI.as_view(), name="application-detail"),
]
