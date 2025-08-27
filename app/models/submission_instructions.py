from django.db import models

from app.models.reports import Report
from app.utils.helper import generateUniqueID


class SubmissionInstruction(models.Model):
    INSTRUCTION_TYPES = [
        ("CERTIFICATE_ONLY", "Certificate Only"),
        ("DEFAULT_RESPONSE", "Default Response"),
        ("RESPONSE_REQUIRED", "Response Required"),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="submission_instruction"
    )
    type = models.CharField(
        max_length=50, choices=INSTRUCTION_TYPES, default="DEFAULT_RESPONSE"
    )
    auto_accept = models.BooleanField(default=False)
    allow_submission = models.BooleanField(
        default=False,
        help_text="Whether submissions are currently allowed for this report",
    )
    questions = models.JSONField(default=dict, blank=True)
    accepted_files = models.JSONField(
        default=list,  # Default empty list for accepted file types
        blank=True,
        help_text="List of accepted file types and their requirements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Instructions for {self.report.name} - {self.type}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
