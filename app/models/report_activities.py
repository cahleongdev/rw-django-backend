from django.db import models

from app.models.reports import Report
from app.models.users import User
from app.utils.helper import generateUniqueID


class ReportActivity(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="activities"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="report_activities"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.first_name}'s activity on {self.report.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
