from django.db import models

import app.constants.options as OPTION_CONSTANT
from app.models.agencies import Agency
from app.models.users import User
from app.utils.helper import generateUniqueID


class ReportCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Color code for the category (e.g., #FF0000)",
    )
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class Report(models.Model):
    SCHEDULE_TYPE_CHOICES = [
        ("SPECIFIC_DATES", "Specific Dates"),
        ("RECURRING_DATES", "Recurring Dates"),
    ]

    RECURRING_PERIOD_CHOICES = [
        ("DAY", "Day"),
        ("WEEK", "Week"),
        ("MONTH", "Month"),
        ("YEAR", "Year"),
        ("QUARTER", "Quarter"),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    report = models.CharField(max_length=200, blank=True)
    file_format = models.JSONField(default=list, blank=True)
    domain = models.CharField(max_length=255, blank=True)

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    categories = models.ManyToManyField(
        ReportCategory, related_name="reports", blank=True
    )

    use_scoring = models.BooleanField(
        default=False, help_text="Whether this report uses scoring criteria"
    )
    schedule_type = models.CharField(
        max_length=50,
        choices=SCHEDULE_TYPE_CHOICES,
        default="SPECIFIC_DATES",
        help_text="Type of scheduling for this report",
    )

    due_date = models.DateTimeField(blank=True, null=True)
    completion_time = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.JSONField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    video_cover = models.URLField(blank=True, null=True)
    file_urls = models.JSONField(default=list, blank=True)
    tag = models.CharField(max_length=50, blank=True, null=True)
    submission_format = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=OPTION_CONSTANT.REPORT_TYPE_CHOICES,
    )
    school_year = models.CharField(max_length=50, blank=True, null=True)

    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_reports",
    )

    # Add new recurring schedule fields
    recurring_period = models.CharField(
        max_length=50,
        choices=RECURRING_PERIOD_CHOICES,
        null=True,
        blank=True,
        help_text="Period for recurring schedules (daily, weekly, monthly, yearly)",
    )
    recurring_interval = models.IntegerField(
        null=True,
        blank=True,
        help_text="Interval between recurring schedules (e.g., every 2 weeks)",
    )
    recurring_occurrences = models.IntegerField(
        null=True, blank=True, help_text="Number of times the schedule should repeat"
    )
    recurring_first_occurrence = models.DateTimeField(
        null=True, blank=True, help_text="Start date for recurring schedules"
    )

    approved = models.BooleanField(
        default=False, help_text="Whether this report has been approved"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)

    def get_schedules(self):
        """Get all schedules for this report"""
        return self.schedules.all().order_by("schedule_time")

    @property
    def get_instruction(self):
        """Get the submission instruction for this report"""
        try:
            return self.submission_instruction
        except:
            return None

    @property
    def get_scoring(self):
        """Get the scoring criteria for this report"""
        try:
            return self.scoring
        except:
            return None
