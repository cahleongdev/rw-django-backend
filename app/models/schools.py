import random
import time

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

import app.constants.options as OPTION_CONSTANT
from app.models.agencies import Agency
from app.models.documents import Document
from app.utils.helper import generateUniqueID


class School(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200, blank=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    gradeserved = ArrayField(models.CharField(max_length=20), blank=True, default=list)
    county = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    number_lea = models.CharField(max_length=50, blank=True, null=True)
    creator = models.EmailField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True)
    network = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, related_name="schools"
    )
    custom_fields = models.JSONField(null=True)
    documents = GenericRelation(Document)
    contact_phone_number = models.CharField(max_length=20, blank=True, null=True)
    contract_expires = models.DateField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    founded_at = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="created_by"
    )
    updated_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="updated_by"
    )

    board_meetings = ArrayField(models.DateField(), blank=True, default=list)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{int(time.time() * 1000)}x{random.randint(100000000000000, 999999999999999)}"
        super().save(*args, **kwargs)
