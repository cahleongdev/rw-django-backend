from django.db import models

from app.models.rubrics import Rubric
from app.models.schools import School
from app.utils.helper import generateUniqueID


class Framework(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class FrameworkSection(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, blank=True, null=True)
    score_types = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.framework.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class RateFramework(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=[
            ("draft", "Draft"),
            ("finalized", "Finalized"),
        ],
    )

    def __str__(self):
        return f"{self.school.name} - {self.framework.title} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
