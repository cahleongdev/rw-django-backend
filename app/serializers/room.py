from rest_framework import serializers

from app.enumeration import RoomType
from app.models.agencies import Agency
from app.models.room import AnnouncementCategory, Room, RoomUser
from app.models.room_messages import RoomMessage
from app.models.users import User
from app.serializers.users import UserSerializer


class AnnouncementCategorySerializer(serializers.ModelSerializer):
    agency_id = serializers.PrimaryKeyRelatedField(
        source="agency", queryset=Agency.objects.all(), required=False
    )

    class Meta:
        model = AnnouncementCategory
        fields = ["id", "name", "color", "agency_id"]
        read_only_fields = ["id"]


class RoomSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    archived = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    announcement_category = AnnouncementCategorySerializer()

    class Meta:
        model = Room
        fields = [
            "id",
            "users",
            "created_at",
            "updated_at",
            "last_message",
            "unread_count",
            "archived",
            "type",
            "announcement_category",
            "title",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_users(self, obj):
        """Get all users in the room with their details"""
        room_users = RoomUser.objects.filter(room=obj).select_related("user")

        users = User.objects.filter(
            id__in=room_users.values_list("user_id", flat=True), deleted_at=None
        )
        users = UserSerializer(users, many=True).data

        return users

    def get_last_message(self, obj):
        """Get the most recent message in the room"""

        if last_message := self.context.get("last_message"):
            return {
                "content": last_message.content,
                "sender": {
                    "id": last_message.sender.id,
                    "first_name": last_message.sender.first_name,
                    "last_name": last_message.sender.last_name,
                },
                "timestamp": last_message.timestamp.isoformat(),
            }

        if (
            last_message := RoomMessage.objects.filter(room=obj)
            .order_by("-timestamp")
            .first()
        ):
            return {
                "content": last_message.content,
                "sender": {
                    "id": last_message.sender.id,
                    "first_name": last_message.sender.first_name,
                    "last_name": last_message.sender.last_name,
                },
                "timestamp": last_message.timestamp,
            }

        return None

    def get_unread_count(self, obj):
        """Get count of unread messages for current user"""
        user_id = self.context.get("user_id")
        if user_id:
            return (
                RoomMessage.objects.filter(room=obj)
                .exclude(read_by__user_id=user_id)
                .count()
            )
        return 0

    def get_archived(self, obj):
        """Get if the room is archived"""

        if user_id := self.context.get("user_id"):
            return RoomUser.objects.get(room=obj, user_id=user_id).archived

        return False

    def get_type(self, obj):
        return RoomType(obj.type).value

    def create(self, validated_data):
        user_ids = self.context.get("user_ids", [])
        request = self.context.get("request")

        if not user_ids:
            raise serializers.ValidationError("No users provided for the room")

        if request and request.user:
            # Create the room
            room = Room.objects.create(**validated_data)

            # Add the current user
            RoomUser.objects.create(room=room, user=request.user)

            # Add other users
            for user_id in user_ids:
                RoomUser.objects.create(room=room, user_id=user_id)

            return room
        raise serializers.ValidationError("User not found in request")


class RoomListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""

    user_names = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "user_names", "last_message", "unread_count", "updated_at"]

    def get_user_names(self, obj):
        """Get list of user names in the room"""
        active_users = obj.users.filter(deleted_at__isnull=True)
        return [user.first_name for user in active_users]

    def get_last_message(self, obj):
        last_message = (
            RoomMessage.objects.filter(room=obj).order_by("-timestamp").first()
        )

        if last_message:
            return {
                "content": (
                    last_message.content[:50] + "..."
                    if len(last_message.content) > 50
                    else last_message.content
                ),
                "sender_name": last_message.sender.first_name,
                "timestamp": last_message.timestamp,
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request and request.user:
            return (
                RoomMessage.objects.filter(room=obj)
                .exclude(read_by__user=request.user)
                .count()
            )
        return 0
