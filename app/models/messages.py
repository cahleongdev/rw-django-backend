from django.db import models
from django.utils import timezone

from app.models.users import User
from app.utils.helper import generateUniqueID


class Message(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sent_messages",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="received_messages",
    )
    file_urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or ""

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
