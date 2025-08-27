from rest_framework import serializers

from app.models.room import Room
from app.models.room_messages import MessageReadBy, RoomMessage
from app.serializers.users import UserFullNameSerializer


class MessageReadBySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = MessageReadBy
        fields = ["id", "message_id", "user", "read_at"]

    def get_user(self, obj):
        user = obj.user
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }


class RoomMessageSerializer(serializers.ModelSerializer):
    sender = UserFullNameSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = RoomMessage
        fields = [
            "id",
            "room",
            "sender",
            "content",
            "timestamp",
            "file_urls",
            "is_read",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_is_read(self, obj):
        """Check if current user has read the message"""
        request = self.context.get("request")
        if not request or not request.user or obj.sender.id == "System":
            return {}

        # Get the read status from the prefetched data
        read_by = getattr(obj, "_prefetched_read_by", None)
        if read_by is not None:
            return MessageReadBySerializer(read_by, many=True).data

        # Fallback to direct query if prefetch wasn't used
        message_read_by = MessageReadBy.objects.filter(message=obj, user=request.user)
        return MessageReadBySerializer(message_read_by, many=True).data

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["sender"] = request.user

            # Create the message
            message = RoomMessage.objects.create(**validated_data)

            # Mark as read by sender automatically
            MessageReadBy.objects.create(message=message, user=request.user)

            return message

        raise serializers.ValidationError("User not found in request")


class RoomMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""

    sender_name = serializers.CharField(source="sender.first_name", read_only=True)
    unread = serializers.SerializerMethodField()

    class Meta:
        model = RoomMessage
        fields = ["id", "sender_name", "content", "timestamp", "unread"]

    def get_unread(self, obj):
        request = self.context.get("request")
        if request and request.user:
            return not MessageReadBy.objects.filter(
                message=obj, user=request.user
            ).exists()
        return True
