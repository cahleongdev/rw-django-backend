from django.db import models

from app.models.agencies import Agency
from app.models.schools import School
from app.models.users import User
from app.utils.helper import generateUniqueID


class Complaint(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    email = models.CharField(max_length=100, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    assigned_member = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    opened_date = models.DateTimeField(blank=True, null=True)
    resolved_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
