from rest_framework import serializers

from app.models.messages import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "receiver",
            "type",
            "title",
            "content",
            "file_urls",
            "created_at",
        ]
        extra_kwargs = {
            "id": {"required": False},
            "created_at": {"required": False},
        }
