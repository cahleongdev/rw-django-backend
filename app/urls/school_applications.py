from django.urls import path

from app.views.school_applications import (
    ApplicationCommentAPI,
    ApplicationMessagePKAPI,
    ApplicationsBySchoolAPI,
    ApplicationSchoolAPI,
    ApplicationSchoolPKAPI,
    ApplicationSchoolSectionAPI,
    ApplicationSchoolSectionPKAPI,
    ApplicationSchoolSubSectionAPI,
    ApplicationSchoolSubSectionPKAPI,
)

urlpatterns = [
    path(
        "detail/<str:pk>/",
        ApplicationSchoolPKAPI.as_view(),
        name="application-school-detail",
    ),
    path(
        "sections/<str:application_school_pk>/",
        ApplicationSchoolSectionAPI.as_view(),
        name="application-school-section",
    ),
    path(
        "section_detail/<str:pk>/",
        ApplicationSchoolSectionPKAPI.as_view(),
        name="application-school-section-detail",
    ),
    path(
        "sub_sections/<str:application_school_pk>/",
        ApplicationSchoolSubSectionAPI.as_view(),
        name="application-sub-section",
    ),
    path(
        "sub_section_detail/<str:pk>/",
        ApplicationSchoolSubSectionPKAPI.as_view(),
        name="application-sub-section-detail",
    ),
    path("comments/", ApplicationCommentAPI.as_view(), name="application-comments"),
    path(
        "messages/<str:application_school_pk>/",
        ApplicationMessagePKAPI.as_view(),
        name="application-message-detail",
    ),
    path(
        "by_school/<str:school_pk>/",
        ApplicationsBySchoolAPI.as_view(),
        name="application-school-by-list",
    ),
    path(
        "<str:application_pk>/",
        ApplicationSchoolAPI.as_view(),
        name="application-school-list",
    ),
]
