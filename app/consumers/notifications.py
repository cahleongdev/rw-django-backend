import ujson

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from app.views.notifications import notification_service


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()

        self.group_name = f"notifications_{self.scope['user'].id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, *args, **kwargs):

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Receive notification would only be for a user to mark a notification as read?

        if not text_data:
            await self.close()

        elif text_data[0] == "d":
            await self._handle_delete_notification(notification_id=text_data[1:])

        elif text_data[0] == "r":
            await self._handle_mark_as_read(notification_id=text_data[1:])

    async def send_notification(self, event):
        message = event["message"]

        await self.send(text_data=ujson.dumps(message))

    @database_sync_to_async
    def _handle_mark_as_read(self, notification_id):
        try:
            notification_service.mark_as_read(notification_id)
        except Exception as e:
            print(e)
            return

    @database_sync_to_async
    def _handle_delete_notification(self, notification_id):
        try:
            notification_service.delete_notification(notification_id)
        except Exception as e:
            print(e)
            return
