from django.db import models

from app.models.reports import Report
from app.utils.helper import generateUniqueID


class ReportScoring(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="scoring"
    )
    exceed = models.TextField(
        blank=True, null=True, help_text="Criteria for Exceeding Expectations"
    )
    meet = models.TextField(
        blank=True, null=True, help_text="Criteria for Meeting Expectations"
    )
    approach = models.TextField(
        blank=True, null=True, help_text="Criteria for Approaching Expectations"
    )
    notmeet = models.TextField(
        blank=True, null=True, help_text="Criteria for Not Meeting Expectations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Scoring Criteria for {self.report.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
