from django.urls import path

from app.views.board_members import (
    BoardMemberListAPI,
    BoardMemberDetailAPI,
    BoardMemberListBySchoolAPI,
    BoardMemberAssignToSchoolAPI,
)

urlpatterns = [
    path('', BoardMemberListAPI.as_view(), name='board-members-all'),
    path('<str:pk>/', BoardMemberDetailAPI.as_view(), name='board-member-detail'),
    path('<str:pk>/schools/', BoardMemberAssignToSchoolAPI.as_view(), name='board-member-assign-to-school'),
    path('schools/<str:school_id>/', BoardMemberListBySchoolAPI.as_view(), name='board-members'),
] 