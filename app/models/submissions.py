from django.db import models

import app.constants.options as OPTION_CONSTANT
from app.models.agencies import Agency
from app.models.report_schedules import ReportSchedule
from app.models.reports import Report
from app.models.schools import School
from app.models.users import User
from app.utils.helper import generateUniqueID


class Submission(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    report_schedule = models.ForeignKey(
        ReportSchedule, on_delete=models.CASCADE, blank=True, null=True
    )
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="incompleted",
    )

    assigned_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_submissions",
    )
    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="evaluated_submissions",
    )
    submission_content = models.JSONField(default=dict, blank=True)
    school_submission_date = models.DateTimeField(blank=True, null=True)
    evaluator_submission_date = models.DateTimeField(blank=True, null=True)
    school_submission_explanation = models.TextField(blank=True, null=True)
    file_urls = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="submission_created_by",
    )
    updated_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="submission_updated_by",
    )

    def __str__(self):
        return f"{self.school.name} - {self.report.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
            self.agency = self.school.agency
        super().save(*args, **kwargs)


class SubmissionMessage(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
