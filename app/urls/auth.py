from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.views.auth import (
    CurrentUserAPI, 
    LoginAPI, 
    LoginMFAVerifyAPI,
    LoginMFASendCodeAPI,
    GetContactInfoAPI,
    SendResetLinkAPI,
    ValidateResetTokenAPI,
    ResetPasswordAPI,
    ValidateInviteTokenAPI,
    AcceptInviteAPI,
    RequestNewMagicLinkAPI,
    GenerateTOTPAPI,
    VerifyTOTPAPI,
    SendMFACodeAPI,
    VerifyBackupCodeAPI,
    GenerateBackupCodesAPI,
    RemoveMFAPI,
    ChangePasswordAPI,
    CustomTokenRefreshView,
)

urlpatterns = [
    path("login/", LoginAPI.as_view(), name="login"),
    path("login/mfa/verify/", LoginMFAVerifyAPI.as_view(), name="login_mfa_verify"),
    path("login/mfa/send_code/", LoginMFASendCodeAPI.as_view(), name="login_mfa_send_code"),
    path("current_user/", CurrentUserAPI.as_view(), name="current-user"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    
    path("change_password/", ChangePasswordAPI.as_view(), name="change_password"),
    
    # Invitation
    path('validate_invite_token/<str:token>/', ValidateInviteTokenAPI.as_view(), name='validate_invite_token'),
    path('accept_invite/', AcceptInviteAPI.as_view(), name='accept_invite'),
    path('request_new_magic_link/', RequestNewMagicLinkAPI.as_view(), name='request_new_magic_link'),
    
    # MFA
    path('mfa/generate/', GenerateTOTPAPI.as_view(), name='generate_totp'),
    path('mfa/verify/', VerifyTOTPAPI.as_view(), name='verify_totp'),
    path('mfa/send_code/', SendMFACodeAPI.as_view(), name='send_mfa_code'),
    path('mfa/verify_backup/', VerifyBackupCodeAPI.as_view(), name='verify_backup_code'),
    path('mfa/generate_backup_codes/', GenerateBackupCodesAPI.as_view(), name='generate_backup_codes'),
    path('mfa/remove/', RemoveMFAPI.as_view(), name='remove_mfa'),

    # Password Reset
    path('contact_info_for_reset/<str:email>/', GetContactInfoAPI.as_view(), name='get_contact_info'),
    path('send_reset_link/', SendResetLinkAPI.as_view(), name='send_reset_link'),
    path('validate_reset_token/<str:token>/', ValidateResetTokenAPI.as_view(), name='validate_reset_token'),
    path('reset_password/', ResetPasswordAPI.as_view(), name='reset_password'),
    
]
