from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.enumeration import RoomType
from app.models.room import AnnouncementCategory, Room, RoomUser
from app.models.room_messages import RoomMessage
from app.models.users import User
from app.serializers.room import (
    AnnouncementCategorySerializer,
    RoomSerializer,
)
from app.serializers.room_messages import RoomMessageSerializer
from app.utils.helper import generateUniqueID


class AnnouncementAPI(APIView):
    @transaction.atomic
    def post(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user_id = token_data["user_id"]

            title = req.data.get("title", "")
            content = req.data.get("content", "")

            # Make sure user is Agency Admin
            current_user = User.objects.get(
                id=current_user_id, deleted_at=None
            )
            if current_user.role != "Agency_Admin":
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get all users from the agency
            users = User.objects.filter(agency=current_user.agency, deleted_at=None)

            req_announcement_category = req.data.get("announcement_category", None)
            db_announcement_category = AnnouncementCategory.objects.get(
                id=req_announcement_category.get("id")
            )
            if not db_announcement_category:
                return Response(
                    {"error": "Announcement category not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Create the room
            room = Room.objects.create(
                type=RoomType.ANNOUNCEMENT.value,
                announcement_category=db_announcement_category,
                title=title,
            )

            # Add all users of the agency to the room
            RoomUser.objects.bulk_create(
                [
                    RoomUser(id=generateUniqueID(), room=room, user=user)
                    for user in users
                ]
            )

            room_message = RoomMessage.objects.create(
                room=room,
                sender=current_user,
                content=content,
            )

            message_data = RoomMessageSerializer(
                room_message, context={"request": req}
            ).data

            room_data = RoomSerializer(
                room, context={"user_id": current_user_id, "last_message": room_message}
            ).data

            channel_layer = get_channel_layer()
            for user in users:
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}", {"type": "create_room", "room": room_data}
                )

                # Send message to the room
                async_to_sync(channel_layer.group_send)(
                    f"chat_{room.id}",
                    {"type": "chat_message", "room_id": room.id, **message_data},
                )

            return Response(room_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": "An error occurred while creating announcement"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AnnouncementCategoryAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]
            agency = User.objects.get(id=user_id, deleted_at=None).agency

            announcement_categories = AnnouncementCategory.objects.filter(
                agency=agency, deleted_at__isnull=True
            )
            serializer = AnnouncementCategorySerializer(
                announcement_categories, many=True
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Error fetching announcement categories"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def put(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]
            agency = User.objects.get(id=user_id, deleted_at=None).agency

            updates = req.data.get("updates", [])
            deletes = req.data.get("deletes", [])
            adds = req.data.get("adds", [])

            for update in updates:
                announcement_category = AnnouncementCategory.objects.get(
                    id=update.get("id"), agency=agency
                )
                for attr, value in update.items():
                    if attr == "id":
                        continue

                    setattr(announcement_category, attr, value)

                announcement_category.save()

            for delete_id in deletes:
                announcement_category = AnnouncementCategory.objects.get(
                    id=delete_id, agency=agency
                )
                announcement_category.delete()

            for add in adds:
                announcement_category = AnnouncementCategory.objects.create(
                    name=add.get("name"),
                    color=add.get("color"),
                    agency=agency,
                )

            announcement_categories = AnnouncementCategory.objects.filter(agency=agency)
            serializer = AnnouncementCategorySerializer(
                announcement_categories, many=True
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Error updating announcement category"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RoomAPI(APIView):

    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]

            rooms = Room.objects.filter(room_users__user=user_id)
            serializer = RoomSerializer(rooms, many=True, context={"user_id": user_id})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching room messages"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def post(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            user_ids = req.data.get("users", [])
            message = req.data.get("message", "")
            title = req.data.get("title", "")

            room = Room.objects.create(title=title)
            RoomUser.objects.create(room=room, user=current_user)

            # Add other users to the room
            for user_id in user_ids:
                if user_id != current_user.id:  # Avoid adding current user twice
                    RoomUser.objects.create(room=room, user_id=user_id)

            room_message = RoomMessage.objects.create(
                id=generateUniqueID(), room=room, sender=current_user, content=message
            )

            room_data = RoomSerializer(
                room, context={"user_id": current_user.id, "last_message": room_message}
            ).data

            message_data = RoomMessageSerializer(room_message).data

            channel_layer = get_channel_layer()
            for user_id in user_ids:
                # New room message
                async_to_sync(channel_layer.group_send)(
                    f"user_{user_id}", {"type": "create_room", "room": room_data}
                )

                # Send message to the room
                async_to_sync(channel_layer.group_send)(
                    f"chat_{room.id}",
                    {"type": "chat_message", "room_id": room.id, **message_data},
                )

            return Response(room_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": "An error occurred while creating the room"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RoomArchiveAPI(APIView):
    def post(self, req, room_id):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]
            archived = req.data.get("archived", False)

            room = Room.objects.get(id=room_id)
            room_user = RoomUser.objects.get(room=room, user_id=user_id)
            room_user.archived = archived
            room_user.save()

            serializer = RoomSerializer(room, context={"user_id": user_id})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while archiving room"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RoomDetailAPI(APIView):
    def get(self, req, room_id):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]

            rooms = Room.objects.filter(id=room_id)
            serializer = RoomSerializer(rooms, many=True, context={"user_id": user_id})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching room details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, req, room_id):

        try:
            token_data = getattr(req, "token_data", None)
            current_user_id = token_data["user_id"]
            room = Room.objects.get(id=room_id)

            if req.data.get("title"):
                room.title = req.data.get("title")

            if user_id := req.data.get("user_id"):
                if not (user := User.objects.get(id=user_id, deleted_at=None)):
                    return Response(
                        {"error": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if RoomUser.objects.filter(room=room, user=user).exists():
                    return Response(
                        {"error": "User already in room"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                room.add_user(user)

                new_message = RoomMessage(
                    id=generateUniqueID(),
                    room=room,
                    sender=User(
                        id="System",
                        first_name="System",
                        last_name="",
                        email="",
                        profile_image="",
                    ),
                    content=f"User {user.first_name} {user.last_name} has been added",
                    timestamp=timezone.now(),
                )

                message_data = RoomMessageSerializer(
                    new_message, context={"request": req}
                ).data

                # Send message to the room to update the room users
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{room.id}",
                    {
                        "room_id": room.id,
                        "user_id": current_user_id,
                        "type": "chat_message",
                        **message_data,
                    },
                )

            return Response(
                RoomSerializer(room, context={"user_id": current_user_id}).data,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An error occurred while updating the room"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
