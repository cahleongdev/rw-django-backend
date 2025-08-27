from asgiref.sync import sync_to_async
from django_tasks import task


from app.models.room import RoomUser
from app.models.room_messages import RoomMessage, MessageReadBy
from app.models.users import User
from app.services.sendgrid import SendGridService
from config.settings import DEFAULT_FROM_EMAIL


@task
def send_email_to_room_users(message_id):
    # Check to see if the meesage has been read
    sendgrid_service = SendGridService()

    message = RoomMessage.objects.get(id=message_id)
    message_read_by = MessageReadBy.objects.filter(message__id=message_id)

    users_not_read = RoomUser.objects.filter(room_id=message.room_id).exclude(
        user_id__in=message_read_by.values_list("user_id", flat=True)
    )

    if len(users_not_read) == 0:
        return

    # Send the email to anyone who hasn't read the message
    full_name = f"{message.sender.first_name} {message.sender.last_name}"
    for user in users_not_read:
        # Send an email to the user
        sendgrid_service.send_email(
            to_email=user.user.email,
            from_email=DEFAULT_FROM_EMAIL,
            subject=f"{full_name} sent you a message",
            content=f"{full_name} sent you a message: {message.content}",
        )
