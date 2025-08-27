from django.db import models
from django.utils import timezone

from app.models.room import Room
from app.models.users import User
from app.utils.helper import generateUniqueID


class RoomMessage(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_room_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file_urls = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["timestamp"]  # Messages will be ordered by time

    def __str__(self):
        return f"Message from {self.sender.first_name} in Room {self.room.id}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class MessageReadBy(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    message = models.ForeignKey(
        RoomMessage, on_delete=models.CASCADE, related_name="read_by"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="read_messages"
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")  # Prevent duplicate reads

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
