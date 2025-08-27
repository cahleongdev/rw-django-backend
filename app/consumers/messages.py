import ujson
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from app.enumeration.room_type import RoomType
from app.models.users import User
from app.models.room import Room, RoomUser
from app.models.room_messages import MessageReadBy, RoomMessage
from app.utils.background_task import send_email_to_room_users
from app.utils.helper import generateUniqueID
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated users
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Join user specific Group
        await self.channel_layer.group_add(
            f"user_{self.scope['user'].id}", self.channel_name
        )

        self.scope["state"]["rooms"] = await self.get_user_rooms()
        for room_id in self.scope["state"]["rooms"]:
            await self.channel_layer.group_add(f"chat_{room_id}", self.channel_name)

        await self.accept()

    async def disconnect(self, *args, **kwargs):
        # Leave room group
        await self.channel_layer.group_discard(
            f"user_{self.scope['user'].id}", self.channel_name
        )

        rooms = self.scope["state"].get("rooms", [])
        for room_id in rooms:
            await self.channel_layer.group_discard(f"chat_{room_id}", self.channel_name)

    async def receive(self, text_data):
        try:

            if text_data[0] == "r":
                await self._handle_read_receipt(text_data)

            else:
                await self._handle_chat_message(text_data)

        except Exception as e:
            print(e)

    async def _handle_read_receipt(self, text_data):
        read_receipt_id = generateUniqueID()
        message_id, room_id = text_data[1:].split("|")

        await self.channel_layer.group_send(
            f"chat_{room_id}",
            {
                "type": "read_receipt",
                "id": read_receipt_id,
                "room_id": room_id,
                "message_id": message_id,
                "user": {
                    "id": self.scope["user"].id,
                    "first_name": self.scope["user"].first_name,
                    "last_name": self.scope["user"].last_name,
                    "email": self.scope["user"].email,
                },
                "read_at": timezone.now().isoformat(),
            },
        )

        await self._db_save_read_receipt(
            read_receipt_id=read_receipt_id,
            message_id=message_id,
            user_id=self.scope["user"].id,
        )

    async def _handle_chat_message(self, text_data):
        message_id = generateUniqueID()
        room_id = text_data.split("|")[0]
        content = "".join(text_data.split("|")[1:])

        message_data = {
            "id": message_id,
            "type": "chat_message",
            "content": content,
            "room_id": room_id,
            "sender": {
                "id": self.scope["user"].id,
                "first_name": self.scope["user"].first_name,
                "last_name": self.scope["user"].last_name,
                "email": self.scope["user"].email,
            },
            "timestamp": timezone.now().isoformat(),
        }

        await self.channel_layer.group_send(
            f"chat_{room_id}",
            message_data,
        )

        await self._db_save_message(message_data)

        await send_email_to_room_users.using(
            run_after=timezone.now()
            + timedelta(minutes=int(settings.MESSAGE_EMAIL_DELAY))
        ).aenqueue(message_data["id"])

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=ujson.dumps(event))

    async def read_receipt(self, event):
        # Send message to WebSocket
        await self.send(text_data=ujson.dumps(event))

    async def create_room(self, event):
        # Have user listen for room messages
        self.scope["state"]["rooms"].append(event["room"]["id"])

        await self.channel_layer.group_add(
            f"chat_{event['room']['id']}", self.channel_name
        )

        # Send message to WebSocket
        await self.send(text_data=ujson.dumps(event))

    @database_sync_to_async
    def get_user_rooms(self):
        return list(
            RoomUser.objects.filter(user=self.scope["user"]).values_list(
                "room_id", flat=True
            )
        )

    @database_sync_to_async
    def is_user_in_room(self, room_id):
        user = self.scope["user"]
        return RoomUser.objects.filter(room_id=room_id, user=user).exists()

    @database_sync_to_async
    def _db_save_read_receipt(self, message_id, read_receipt_id, user_id):
        MessageReadBy.objects.create(
            id=read_receipt_id,
            message=RoomMessage.objects.get(id=message_id),
            user=User.objects.get(id=user_id),
        )

    @database_sync_to_async
    def _db_save_message(self, message_data):
        # Need to delay this creation to avoid race condition
        room = Room.objects.get(id=message_data["room_id"])

        sender = User.objects.get(id=message_data["sender"]["id"])

        RoomMessage.objects.create(
            id=message_data["id"],
            room=room,
            sender=sender,
            content=message_data["content"],
            timestamp=message_data["timestamp"],
        )
