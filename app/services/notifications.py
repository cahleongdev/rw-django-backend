from collections import defaultdict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import boto3
from boto3.dynamodb.conditions import Key
from django.conf import settings

import app.constants.msg as MSG_CONSTANT
from app.enumeration import NotificationType
from app.models.applications import Application

# from app.models.comments import Comment
from app.models.complaints import Complaint
from app.models.notifications import Notification
from app.models.reports import Report
from app.models.schools import School
from app.models.users import User
from app.serializers.notifications import NotificationSerializer
from app.services.aws_mock import mock_aws_service


class NotificationService:
    def __init__(self):
        # Use mock AWS service instead of direct boto3 calls
        self.dynamodb = mock_aws_service.get_dynamodb_resource()
        self.dynamodb_client = mock_aws_service.get_dynamodb_client()
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME or 'notifications')

    def _format_value(self, value):
        if isinstance(value, str):
            return {"S": value}
        elif isinstance(value, bool):
            return {"BOOL": value}
        elif isinstance(value, (int, float)):
            return {"N": str(value)}
        elif isinstance(value, list) or isinstance(value, set):
            return {"L": [self._format_value(item) for item in value]}
        elif value is None:
            return {"NULL": True}
        elif isinstance(value, dict):
            return {"M": {k: self._format_value(v) for k, v in value.items()}}
        else:
            return {"S": str(value)}

    def _batch_create_notifications(self, notifications: list[Notification]):
        notifications_data = NotificationSerializer(notifications, many=True).data

        formatted_notifications = [
            {
                "PutRequest": {
                    "Item": {k: self._format_value(v) for k, v in notification.items()}
                }
            }
            for notification in notifications_data
        ]

        self.dynamodb_client.batch_write_item(
            RequestItems={settings.DYNAMODB_TABLE_NAME: formatted_notifications}
        )

        self.send_notification_through_websocket(notifications_data)

    def create_notifications(
        self,
        notifications: list[Notification],
        create_batch=False,
    ):
        if not notifications:
            return

        built_notifications = self._build_notification_links(
            notifications,
        )

        if create_batch:
            self._batch_create_notifications(built_notifications)

        else:
            notifications_data = NotificationSerializer(built_notifications).data
            self.table.put_item(Item=notifications_data[0])

            self.send_notification_through_websocket(notifications_data)

    def send_notification_through_websocket(self, notifications_data):

        channel_layer = get_channel_layer()
        for notification in notifications_data:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{notification['receiver_id']}",
                {
                    "type": "send_notification",
                    "message": notification,
                },
            )

    def get_created_at(self, notification_id):
        response = self.table.query(
            KeyConditionExpression=Key("id").eq(notification_id)
        )
        if not response.get("Items"):
            return None

        return response["Items"][0]["created_at"]

    def get_notifications(self, receiver_id):
        response = self.table.scan(
            FilterExpression="receiver_id = :receiver_id",
            ExpressionAttributeValues={":receiver_id": receiver_id},
        )
        return response.get("Items", [])

    def mark_as_read(self, notification_id):
        created_at = self.get_created_at(notification_id)
        if not created_at:
            return {"error": "Notification not found"}

        self.table.update_item(
            Key={"id": notification_id, "created_at": created_at},
            UpdateExpression="SET #read = :read",
            ExpressionAttributeNames={"#read": "read"},
            ExpressionAttributeValues={":read": True},
        )
        return {"message": MSG_CONSTANT.MSG_NOTIFICATINO_MARKED_READ}

    def delete_notification(self, notification_id):
        created_at = self.get_created_at(notification_id)
        if not created_at:
            return {"error": MSG_CONSTANT.MSG_NOTIFNOTIFICATION_NOT_FOUND}

        self.table.delete_item(Key={"id": notification_id, "created_at": created_at})
        return {"message": MSG_CONSTANT.MSG_NOTIFICATION_DELETED}

    def _build_notification_links(
        self,
        notifications,
    ) -> list[Notification]:

        notification_map = {
            notification.id: notification for notification in notifications
        }

        report_id_notifciation_map = defaultdict(list)
        school_id_notifciation_map = defaultdict(list)
        comment_id_notifciation_map = defaultdict(list)
        complaint_id_notifciation_map = defaultdict(list)
        application_id_notifciation_map = defaultdict(list)
        new_user_id_notifciation_map = defaultdict(list)

        for notification in notifications:
            # Validate required parameters for each notification type
            if notification.type in [
                NotificationType.REPORT_ASSIGNMENT,
                NotificationType.REPORT_UNASSIGNMENT,
                NotificationType.NEW_COMMENTS,
                NotificationType.REPORT_SUBMISSION,
                NotificationType.MULTIPLE_REPORT_ASSIGNMENT,
                NotificationType.MULTIPLE_REPORT_UNASSIGNMENT,
            ]:
                if not notification.report_id:
                    raise ValueError(
                        f"report_id is required for notification type: {notification.type}"
                    )

                report_id_notifciation_map[notification.report_id].append(
                    notification.id
                )

            if notification.type in [
                NotificationType.REPORT_ASSIGNMENT,
                NotificationType.REPORT_UNASSIGNMENT,
                NotificationType.REPORT_SUBMISSION,
                NotificationType.NEW_SCHOOL_USERS,
                NotificationType.SCHOOL_INFO_UPDATE,
                NotificationType.BOARD_CALENDAR_UPDATE,
                NotificationType.APPLICATION_SUBMISSION,
                NotificationType.APPLICATION_EVALUATION,
                NotificationType.MULTIPLE_REPORT_ASSIGNMENT,
                NotificationType.MULTIPLE_REPORT_UNASSIGNMENT,
            ]:
                if not notification.school_ids:
                    raise ValueError(
                        f"school_ids is required for notification type: {notification.type}"
                    )

                for school_id in notification.school_ids:
                    school_id_notifciation_map[school_id].append(notification.id)

            if notification.type == NotificationType.NEW_COMMENTS:
                if not notification.comment_id:
                    raise ValueError(
                        "comment_id is required for NEW_COMMENTS notification type"
                    )

                comment_id_notifciation_map[notification.comment_id].append(
                    notification.id
                )

            if notification.type in [
                NotificationType.APPLICATION_SUBMISSION,
                NotificationType.APPLICATION_EVALUATION,
            ]:
                if not notification.application_id:
                    raise ValueError(
                        f"application_id is required for notification type: {notification.type}"
                    )

                application_id_notifciation_map[notification.application_id].append(
                    notification.id
                )

            if notification.type == NotificationType.COMPLAINT_ASSIGNMENT:
                if not notification.complaint_id:
                    raise ValueError(
                        "complaint_id is required for COMPLAINT_ASSIGNMENT notification type"
                    )
                complaint_id_notifciation_map[notification.complaint_id].append(
                    notification.id
                )

            if notification.type in [
                NotificationType.NEW_AGENCY_USER,
                NotificationType.NEW_SCHOOL_USERS,
            ]:
                if not notification.new_user_id:
                    raise ValueError(
                        "new_user_id is required for NEW_AGENCY_USER notification type"
                    )

                new_user_id_notifciation_map[notification.new_user_id].append(
                    notification.id
                )

        # if comment_id_notifciation_map:
        #     for comment in Comment.objects.filter(id__in=comment_id_notifciation_map.keys()):
        #         for notification_id in comment_id_notifciation_map[comment.id]:
        #             notification_map[notification_id].links.append({"type": "comment", "id": comment.id, "label": comment.content})

        if report_id_notifciation_map:
            for report in Report.objects.filter(
                id__in=report_id_notifciation_map.keys()
            ):
                for notification_id in report_id_notifciation_map[report.id]:
                    notification_map[notification_id].links.append(
                        {"entityType": "report", "id": report.id, "label": report.name}
                    )

        if school_id_notifciation_map:
            for school in School.objects.filter(
                id__in=school_id_notifciation_map.keys()
            ).order_by("name"):
                for notification_id in school_id_notifciation_map[school.id]:
                    notification_map[notification_id].links.append(
                        {"entityType": "school", "id": school.id, "label": school.name}
                    )

        if complaint_id_notifciation_map:
            for complaint in Complaint.objects.filter(
                id__in=complaint_id_notifciation_map.keys()
            ):
                for notification_id in complaint_id_notifciation_map[complaint.id]:
                    notification_map[notification_id].links.append(
                        {
                            "entityType": "complaint",
                            "id": complaint.id,
                            "label": complaint.title,
                        }
                    )

        if application_id_notifciation_map:
            for application in Application.objects.filter(
                id__in=application_id_notifciation_map.keys()
            ):
                for notification_id in application_id_notifciation_map[application.id]:
                    notification_map[notification_id].links.append(
                        {
                            "entityType": "application",
                            "id": application.id,
                            "label": application.title,
                        }
                    )

        if new_user_id_notifciation_map:
            for new_user in User.objects.filter(
                id__in=new_user_id_notifciation_map.keys(), deleted_at=None
            ):
                for notification_id in new_user_id_notifciation_map[new_user.id]:
                    notification_map[notification_id].links.append(
                        {
                            "entityType": "user",
                            "id": new_user.id,
                            "label": f"{new_user.first_name} {new_user.last_name}",
                        }
                    )

        return list(notification_map.values())
