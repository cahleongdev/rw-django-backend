from django.contrib.postgres.fields import ArrayField
from django.db import models

from app.utils.helper import generateUniqueID


class Agency(models.Model):
    JURISDICTIONS = [
        ("State", "State"),
        ("Country", "Country"),
        ("City", "City"),
        ("Other", "Other"),
    ]
    AUTHROIZE_TYPES = [
        ("University", "University"),
        ("County", "County"),
        ("District", "District"),
        ("State-Wide", "State-Wide"),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(
        max_length=255, unique=True, null=True,
    )
    admin_privileges = ArrayField(
        models.CharField(max_length=100), blank=True, default=list
    )
    school_privileges = ArrayField(
        models.CharField(max_length=100), blank=True, default=list
    )
    access_school = models.BooleanField(default=False)
    home_url = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True, default="")
    city = models.CharField(max_length=255, blank=True, null=True, default="")
    state = models.CharField(max_length=255, blank=True, null=True, default="")
    county = models.CharField(max_length=255, blank=True, null=True, default="")
    zipcode = models.CharField(max_length=255, blank=True, null=True, default="")
    years_operation = models.CharField(
        max_length=255, blank=True, null=True, default=""
    )
    authorize_type = models.CharField(
        max_length=255, choices=AUTHROIZE_TYPES, blank=True, null=True
    )
    jurisdiction = models.CharField(
        max_length=255, choices=JURISDICTIONS, blank=True, null=True
    )
    calendar_year = models.DateField(blank=True, null=True)
    number_of_schools = models.IntegerField(blank=True, null=True)
    number_of_impacted_students = models.IntegerField(blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    annual_budget = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    custom_fields = models.JSONField(default=dict)

    agency_entity_fields = models.JSONField(default=dict)
    school_entity_fields = models.JSONField(default=dict)
    network_entity_fields = models.JSONField(default=dict)
    board_member_fields = models.JSONField(default=dict)
    agency_user_fields = models.JSONField(default=dict)
    school_user_fields = models.JSONField(default=dict)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generateUniqueID()
        super().save(*args, **kwargs)
