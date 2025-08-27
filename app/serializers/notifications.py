from rest_framework import serializers

from app.enumeration import NotificationType
from app.models.notifications import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    school_ids = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "description",
            "type",
            "receiver_id",
            "read",
            "report_id",
            "comment_id",
            "school_ids",
            "created_at",
            "links",
        ]
        extra_kwargs = {
            "id": {"required": False},
            "created_at": {"required": False},
            "updated_at": {"required": False},
        }

    def get_type(self, obj):
        if isinstance(obj, Notification):
            return obj.type.value.lower()

        return obj.get("type").split(".")[-1].lower()

    def get_school_ids(self, obj):
        if isinstance(obj, Notification):
            return list(obj.school_ids)

        return list(obj.get("school_ids"))
