from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import Extract
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.query import Prefetch

from app.models.room import Room, RoomUser
from app.models.room_messages import MessageReadBy, RoomMessage
from app.models.users import User
from app.serializers.room_messages import (
    MessageReadBySerializer,
    RoomMessageSerializer,
)
from app.utils.helper import generateUniqueID
from app.utils.background_task import send_email_to_room_users
from datetime import timedelta
from django.conf import settings


class RoomMessagesAPI(APIView):
    def get(self, request: Request, room_id: str):
        try:
            # Get the user instance
            token_data = request.token_data
            user_id = token_data["user_id"]
            current_user = get_object_or_404(User, id=user_id)

            # Optimize the query with prefetch_related
            messages = (
                RoomMessage.objects.filter(room_id=room_id)
                .select_related("sender")
                .prefetch_related(
                    Prefetch(
                        "read_by",
                        queryset=MessageReadBy.objects.filter(
                            user=current_user
                        ).select_related("user"),
                        to_attr="_prefetched_read_by",
                    )
                )
            )

            # Get all existing MessageReadBy records for these messages and current user
            message_ids = messages.values_list("id", flat=True)
            existing_read_records = (
                MessageReadBy.objects.filter(
                    message__id__in=message_ids,
                    user=current_user,
                )
            ).values_list("message_id", flat=True)

            # Create MessageReadBy records for messages that don't have one
            new_read_records = [
                message
                for message in messages
                if message.id not in existing_read_records
            ]

            if new_read_records:
                entries = [
                    MessageReadBy(
                        id=generateUniqueID(), message=message, user=current_user
                    )
                    for message in new_read_records
                ]

                message_read_by = MessageReadBy.objects.bulk_create(entries)
                message_read_by_data = MessageReadBySerializer(message_read_by[-1]).data

                # Send message through WebSocket of last message to update Read Receipt
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{room_id}",
                    {
                        "type": "read_receipt",
                        "room_id": room_id,
                        **message_read_by_data,
                    },
                )

            messages = list(messages)

            # Check if users have been added to the room after creation:
            if user_data := self._check_after_the_fact_user_add(room_id):
                new_messages = [
                    RoomMessage(
                        id=generateUniqueID(),
                        room=Room.objects.get(id=room_id),
                        sender=User(
                            id="System",
                            first_name="System",
                            last_name="",
                            email="",
                            profile_image="",
                        ),
                        content=f"User {user.user.first_name} {user.user.last_name} has been added",
                        timestamp=user.joined_at,
                    )
                    for user in user_data
                ]

                messages.extend(new_messages)

            messages.sort(key=lambda x: x.timestamp)

            response = RoomMessageSerializer(
                messages, many=True, context={"request": request}
            ).data

            return Response(response)
        except Exception as e:
            return Response(
                {"error": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request: Request, room_id: str):
        try:
            token_data = request.token_data
            current_user_id = token_data.get("user_id")
            context = {"request": request}

            serializer = RoomMessageSerializer(
                data=request.data | {"room": room_id}, context=context
            )

            if serializer.is_valid():
                message = serializer.save()

                # Send message through WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{room_id}",
                    {
                        "user_id": current_user_id,
                        "type": "chat_message",
                        "room_id": room_id,
                        **serializer.data,
                    },
                )

                send_email_to_room_users.using(
                    run_after=timezone.now()
                    + timedelta(minutes=int(settings.MESSAGE_EMAIL_DELAY))
                ).enqueue(message.id)

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An error occurred while creating the message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _check_after_the_fact_user_add(self, room_id: str):
        # If the time difference is greater than 0, then the user was added after the room was created
        time_diff_minutes = RoomUser.objects.annotate(
            time_difference_minutes=ExpressionWrapper(
                (Extract(F("joined_at") - F("room__created_at"), "epoch") / 60),
                output_field=FloatField(),
            )
        ).filter(room_id=room_id, time_difference_minutes__gt=1)

        return time_diff_minutes


class MarkMessageAsReadAPI(APIView):
    def post(self, request: Request, room_id: str, message_id: str):
        try:
            token_data = request.token_data
            user_id = token_data["user_id"]

            # Get the user instance
            user = get_object_or_404(User, id=user_id)
            message = get_object_or_404(RoomMessage, id=message_id)

            message_read_by = MessageReadBy.objects.get_or_create(
                message=message, user=user
            )

            if message_read_by[1]:
                message_read_by_data = MessageReadBySerializer(message_read_by[0]).data

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{room_id}",
                    {
                        "type": "read_receipt",
                        "room_id": room_id,
                        "user_id": user_id,
                        **message_read_by_data,
                    },
                )

                return Response(message_read_by_data)

            return Response({"status": "already read"})

        except Exception as e:
            print(e)
            return Response(
                {"error": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
