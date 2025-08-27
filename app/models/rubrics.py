from django.db import models

from app.utils.helper import generateUniqueID


class Rubric(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class Score(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    score = models.CharField(max_length=255)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - Score: {self.score}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
