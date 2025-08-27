from django.db import models

from app.models.agencies import Agency
from app.models.schools import School
from app.utils.helper import generateUniqueID


class BoardMember(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    schools = models.ManyToManyField(
        School, 
        related_name='board_members'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    start_term = models.DateField(blank=True, null=True)
    end_term = models.DateField(blank=True, null=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs) 