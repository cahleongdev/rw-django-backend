from datetime import datetime, timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.enumeration import NotificationType
from app.models.notifications import Notification
from app.serializers.notifications import NotificationSerializer
from app.services.notifications import NotificationService
from app.services.users import get_notification_settings
from app.utils.helper import generateUniqueID

notification_service = NotificationService()


class CreateNotificationView(APIView):
    def post(self, request):
        description = request.data.get("description")
        request_type = request.data.get("type")
        type = NotificationType(request_type)

        key = request.data.get("key")

        # How to determine the receiver_id?
        receiver_id = request.data.get("receiver_id")
        report_id = request.data.get("report_id")
        comment_id = request.data.get("comment_id")
        school_id = request.data.get("school_id")

        if not description or not receiver_id:
            return Response(
                {"error": MSG_CONST.MSG_NOTIFICATION_VALIDATION["required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = notification_service.create_notifications(
            notifications=[
                Notification(
                    id=generateUniqueID(),
                    description=description,
                    type=type,
                    receiver_id=receiver_id,
                    report_id=report_id,
                    comment_id=comment_id,
                    school_ids=[school_id],
                    created_at=datetime.now(timezone.utc),
                )
            ]
        )

        return Response(notification, status=status.HTTP_201_CREATED)


class GetNotificationsView(APIView):
    def get(self, _, receiver_id):
        notifications = notification_service.get_notifications(receiver_id)
        notifications = NotificationSerializer(notifications, many=True).data
        return Response({"notifications": notifications}, status=status.HTTP_200_OK)


class MarkReadNotificationView(APIView):
    def put(self, _, notification_id):
        result = notification_service.mark_as_read(notification_id)
        return Response(result, status=status.HTTP_200_OK)


class NotificationPKAPI(APIView):

    def put(self, _, notification_id):
        result = notification_service.mark_as_read(notification_id)
        return Response(result, status=status.HTTP_200_OK)

    def delete(self, _, notification_id):
        try:
            result = notification_service.delete_notification(notification_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting notification"},
                status=status.HTTP_400_BAD_REQUEST,
            )
