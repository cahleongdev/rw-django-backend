from django.db import models

from app.enumeration import RoomType
from app.models.users import User
from app.models.agencies import Agency
from app.utils.helper import generateUniqueID


class AnnouncementCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name="announcement_categories",
        null=True,
    )
    name = models.CharField(max_length=255, null=False)
    color = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.agency.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()

        super().save(*args, **kwargs)


class Room(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    announcement_category = models.ForeignKey(
        AnnouncementCategory,
        on_delete=models.SET_NULL,
        related_name="rooms",
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=50, choices=RoomType.choices(), default=RoomType.MESSAGE.value
    )

    def __str__(self):
        user_names = [user.first_name for user in self.get_users()]
        return f"Chat Room {self.id} - {', '.join(user_names)}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)

    def get_users(self):
        """Get all users in this room"""
        active_users = User.objects.filter(room_users__room=self, deleted_at__isnull=True)
        return active_users

    def add_user(self, user):
        """Add a user to the room"""
        RoomUser.objects.get_or_create(room=self, user=user)

    def remove_user(self, user):
        """Remove a user from the room"""
        RoomUser.objects.filter(room=self, user=user).delete()


class RoomUser(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_users")
    joined_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ("room", "user")  # Prevent duplicate entries

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
