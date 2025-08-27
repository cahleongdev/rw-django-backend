from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta, datetime
from urllib.parse import urlparse

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from app.models.users import User
from app.serializers.users import UserNotifcationSettingSerializer
from app.services.sendgrid import SendGridService
from app.services.notifications import NotificationService

from app.enumeration.user_role import UserRole
from app.enumeration.notification_type import NotificationType

from app.models.notifications import Notification

from app.utils.helper import generateUniqueID


def get_notification_settings(userId):

    user = get_object_or_404(User, pk=userId)
    serializer = UserNotifcationSettingSerializer(user)

    return serializer.data


def generate_token_code(user, inviting_user):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    user.invitation_token = token
    user.invitation_token_expires_at = timezone.now() + timedelta(
        hours=24
    )  # invite link expires in 24 hours
    user.invitated_by = inviting_user
    user.save()

    return token


def send_invitation_email(request, user, inviting_user, token):

    # Get frontend URL from request
    referer = request.META.get("HTTP_REFERER", "")
    if referer:
        parsed_url = urlparse(referer)
        frontend_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    else:
        frontend_url = request.build_absolute_uri("/")[:-1]

    invitation_url = f"{frontend_url}/signup?token={token}"
    request_new_link_url = f"{frontend_url}/request-new-magic-link?userId={user.id}"

    # Send invitation email
    sendgrid_service = SendGridService()
    email_content = f"""
        <h2>You've been invited to ReportWell</h2>
        <p>You have been invited by {inviting_user.get_full_name()} to join ReportWell.</p>
        <p>Click the link below to set your password and activate your account:</p>
        <p><a href="{invitation_url}">{invitation_url}</a></p>
        <p>This link will expire in 24 hours. Please click <a href="{request_new_link_url}">here</a> to request a new one.</p>
        <p>If you have questions or have any issues, please email us at <a href="mailto:support@reportwell.io">support@reportwell.io</a> and we will happily assist.</p>
    """
    sendgrid_service.send_email(
        from_email=None,
        to_email=user.email,
        subject="Invitation to ReportWell",
        content=email_content,
    )

def send_user_notifications(new_user):
    """Send notifications to relevant users when a new user is created"""
    notification_service = NotificationService()
    new_user_role = UserRole(new_user.role)

    if new_user_role in [UserRole.SCHOOL_USER, UserRole.SCHOOL_ADMIN]:
        # Get school IDs as a list
        school_ids = list(new_user.schools.values_list('id', flat=True))
        
        notification_service.create_notifications(
            notifications=[
                Notification(
                    id=generateUniqueID(),
                    description=f"School updated: {new_user.first_name} {new_user.last_name}",
                    type=NotificationType.NEW_SCHOOL_USERS,
                    receiver_id=user.id,
                    school_ids=school_ids,
                    new_user_id=new_user.id,
                    created_at=datetime.now(),
                )
                for user in User.objects.filter(
                    schools__id__in=school_ids,
                    deleted_at=None,
                ).exclude(id=new_user.id)  # Don't notify the new user themselves
            ],
            create_batch=True,
        )

    elif new_user_role in [UserRole.AGENCY_USER, UserRole.AGENCY_ADMIN]:
        notification_service.create_notifications(
            notifications=[
                Notification(
                    id=generateUniqueID(),
                    description=f"Agency updated: {new_user.first_name} {new_user.last_name}",
                    type=NotificationType.NEW_AGENCY_USER,
                    new_user_id=new_user.id,
                    receiver_id=user.id,
                    agency_id=new_user.agency.id if new_user.agency else None,
                    created_at=datetime.now(),
                )
                for user in User.objects.filter(
                    agency_id=new_user.agency.id if new_user.agency else None,
                    role__in=[
                        UserRole.AGENCY_USER.value,
                        UserRole.AGENCY_ADMIN.value,
                    ],
                    deleted_at=None,
                ).exclude(id=new_user.id)  # Don't notify the new user themselves
            ],
            create_batch=True,
        )


def user_invitation(req, new_user, inviting_user):
    token = generate_token_code(new_user, inviting_user)
    send_invitation_email(req, new_user, inviting_user, token)

    
