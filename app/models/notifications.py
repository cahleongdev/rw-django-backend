from django.db import models

from app.utils.helper import generateUniqueID


class Notification(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    receiver_id = models.CharField(max_length=50, blank=True, null=True)
    read = models.BooleanField(default=False)
    type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    links = models.JSONField(default=list, null=True)
    report_id = models.CharField(max_length=50, blank=True, null=True)
    comment_id = models.CharField(max_length=50, blank=True, null=True)
    complaint_id = models.CharField(max_length=50, blank=True, null=True)
    application_id = models.CharField(max_length=50, blank=True, null=True)
    school_ids = models.JSONField(default=list, null=True)
    agency_id = models.CharField(max_length=50, blank=True, null=True)
    new_user_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
