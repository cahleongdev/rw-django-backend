from django.db import models

import app.constants.options as OPTION_CONST
from app.models.agencies import Agency
from app.models.rubrics import Rubric, Score
from app.models.schools import School
from app.models.users import User
from app.utils.helper import generateUniqueID


class Application(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationSection(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, blank=True, null=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.application.name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationSubSection(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application_section = models.ForeignKey(
        ApplicationSection, on_delete=models.CASCADE, blank=True, null=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationQuestion(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application_sub_section = models.ForeignKey(
        ApplicationSubSection, on_delete=models.CASCADE, blank=True, null=True
    )
    type = models.CharField(
        max_length=50,
        choices=OPTION_CONST.APPLICATION_SUBSECTION_QUESTION_TYPES,
        default=("short_text", "Short Text"),
    )
    content = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


# -------------------------------------------------------School Application Part---------------------------------------------------------- #


class ApplicationSchool(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50, blank=True, null=True, default="incompleted"
    )
    submission_time = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("application", "school")

    def __str__(self):
        return f"{self.application.name} - {self.school.name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationSchoolSection(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application_school = models.ForeignKey(
        ApplicationSchool, null=False, blank=False, on_delete=models.CASCADE
    )
    application_section = models.ForeignKey(
        ApplicationSection, null=False, blank=False, on_delete=models.CASCADE
    )
    grad = models.ForeignKey(Score, blank=True, null=True, on_delete=models.CASCADE)
    assigned_member = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=50,
        choices=OPTION_CONST.APPLICATION_STATUS_OPTIONS,
        default=("incompleted", "Incompleted"),
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationSchoolSubSection(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application_school = models.ForeignKey(
        ApplicationSchool, null=False, blank=False, on_delete=models.CASCADE
    )
    application_sub_section = models.ForeignKey(
        ApplicationSubSection, null=False, blank=False, on_delete=models.CASCADE
    )
    grad = models.ForeignKey(Score, blank=True, null=True, on_delete=models.CASCADE)
    assigned_member = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=50,
        choices=OPTION_CONST.APPLICATION_STATUS_OPTIONS,
        default=("incompleted", "Incompleted"),
    )
    answers = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationMessage(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application_school = models.ForeignKey(
        ApplicationSchool, null=False, blank=False, on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class ApplicationComment(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    application_school = models.ForeignKey(
        ApplicationSchool, null=True, blank=True, on_delete=models.CASCADE
    )
    application_school_section = models.ForeignKey(
        ApplicationSchoolSection, null=True, blank=True, on_delete=models.CASCADE
    )
    application_school_sub_section = models.ForeignKey(
        ApplicationSchoolSubSection, null=True, blank=True, on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
