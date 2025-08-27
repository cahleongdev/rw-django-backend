from django.db import models

from app.models.agencies import Agency
from app.models.reports import Report
from app.models.users import User
from app.utils.helper import generateUniqueID


class TransparencyDetail(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

    help_faqs_url = models.TextField(blank=True, null=True)
    contact_form_url = models.TextField(blank=True, null=True)
    privacy_policy_url = models.TextField(blank=True, null=True)
    website_homepage_url = models.TextField(blank=True, null=True)
    custom_domain_url = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone_number = models.CharField(max_length=20, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.agency.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class TransparencyFolder(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.TextField(blank=True, null=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="folders_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="folders_updated"
    )

    def __str__(self):
        return f"{self.agency.name} - {self.report.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()

        super().save(*args, **kwargs)


class TransparencySubFolder(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.TextField(blank=True, null=True)
    folder = models.ForeignKey(TransparencyFolder, on_delete=models.CASCADE)
    reports = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sub_folders_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sub_folders_updated"
    )

    def __str__(self):
        return f"{self.folder.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)


class TransparencyReport(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    sub_folder = models.ForeignKey(TransparencySubFolder, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sub_folder.name} - {self.report.name}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
