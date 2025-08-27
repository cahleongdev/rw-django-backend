from django.db import models

from app.models.reports import Report
from app.utils.helper import generateUniqueID


class ReportSchedule(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="schedules"
    )
    schedule_time = models.DateTimeField()
    report_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["schedule_time"]

    def __str__(self):
        return f"{self.report_name} - {self.schedule_time}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
