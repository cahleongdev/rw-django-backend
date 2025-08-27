from django.urls import path

from app.views.frameworks import (
    FrameworkAPI,
    FrameworkPKAPI,
    FrameworkSectionAPI,
    FrameworkSectionPKAPI,
    RateFrameworkAPI,
    RateFrameworkPKAPI,
)

urlpatterns = [
    path("", FrameworkAPI.as_view(), name="framework-list"),
    path("rate/", RateFrameworkAPI.as_view(), name="rateframework-list"),
    path("rate/<str:pk>/", RateFrameworkPKAPI.as_view(), name="rateframework-detail"),
    path("<str:pk>/", FrameworkPKAPI.as_view(), name="framework-list"),
    path(
        "section/<str:framework_pk>/",
        FrameworkSectionAPI.as_view(),
        name="framework-section-list",
    ),
    path(
        "section_detail/<str:pk>/",
        FrameworkSectionPKAPI.as_view(),
        name="framework-section-detail",
    ),
]
