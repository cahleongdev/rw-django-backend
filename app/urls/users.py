from django.urls import path

from app.views.users import (
    MessageUsersAPI,
    SchoolUserAPI,
    SuperAdminUsersAPI,
    AgencyAdminUserAPI,
    SchoolAdminUserAPI,
    UserCreateAPI,
    UserPKAPI,
    UserMFAContactAPI,
    UserMeAPI,
)

urlpatterns = [
    path("", UserCreateAPI.as_view(), name="user-create"),
    path(
        "school_users/<str:role>/<str:school>/",
        SchoolUserAPI.as_view(),
        name="school-user-detail",
    ),
    path(
        "school_admin/<str:school>/",
        SchoolAdminUserAPI.as_view(),
        name="user-school-admin",
    ),
    path("agency_admin/", AgencyAdminUserAPI.as_view(), name="user-agency-admin"),
    path("super_admin/", SuperAdminUsersAPI.as_view(), name="user-super-admin"),
    path("message_users/", MessageUsersAPI.as_view(), name="message-users"),
    path("mfa_contact/", UserMFAContactAPI.as_view(), name="user-mfa-contact"),
    path("me/", UserMeAPI.as_view(), name="user-me"),
    path("<str:pk>/", UserPKAPI.as_view(), name="user-detail"),
]
