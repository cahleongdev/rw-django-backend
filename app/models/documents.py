from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from app.utils.helper import generateUniqueID


class Document(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    file_url = models.CharField(max_length=255, null=True, blank=True)

    parent_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_id = models.CharField(max_length=50)
    parent_object = GenericForeignKey("parent_type", "parent_id")

    type = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.parent_type.model} document)"
