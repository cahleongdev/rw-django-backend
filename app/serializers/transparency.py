from rest_framework import serializers

from app.models.reports import Report
from app.models.transparency import (
    TransparencyDetail,
    TransparencyFolder,
    TransparencySubFolder,
    TransparencyReport,
)
from app.models.schools import School

from datetime import datetime


class TransparencyReportSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    due_date = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    file_urls = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "name",
            "due_date",
            "year",
            "file_urls",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def get_name(self, obj):
        if isinstance(obj, TransparencyReport):
            return obj.report.name

        return obj.name

    def get_due_date(self, obj):
        if isinstance(obj, TransparencyReport):
            return (
                obj.report.due_date.strftime("%B %d, %Y")
                if obj.report.due_date
                else None
            )

        return obj.due_date.strftime("%B %d, %Y") if obj.due_date else None

    def get_year(self, obj):
        if isinstance(obj, TransparencyReport):
            return obj.report.due_date.year if obj.report.due_date else None

        return obj.due_date.year if obj.due_date else None

    def get_file_urls(self, obj):
        if isinstance(obj, TransparencyReport):
            return obj.report.file_urls

        return obj.file_urls if obj.file_urls else []


class TransparencyDetailsSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(source="agency.street_address")
    city = serializers.CharField(source="agency.city")
    state = serializers.CharField(source="agency.state")
    zipcode = serializers.CharField(source="agency.zipcode")
    logo_url = serializers.CharField(source="agency.logo_url")
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = TransparencyDetail
        fields = [
            "logo_url",
            "help_faqs_url",
            "contact_form_url",
            "privacy_policy_url",
            "website_homepage_url",
            "custom_domain_url",
            "contact_phone_number",
            "contact_email",
            "street_address",
            "city",
            "state",
            "zipcode",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = ["id", "updated_at", "updated_by"]

    def save(self, **kwargs):
        return super().save(**kwargs)

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%B %d, %Y")

    def update(self, instance, validated_data):
        agency_data = validated_data.pop("agency", {})
        agency = instance.agency

        # Update agency fields
        if agency_data:
            for attr, value in agency_data.items():
                setattr(agency, attr, value)
            agency.save()

        # Update TransparencyDetail fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class TransparencyFolderSerializer(serializers.ModelSerializer):
    subFolders = serializers.SerializerMethodField()

    class Meta:
        model = TransparencyFolder
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "subFolders",
        ]

    def get_subFolders(self, obj):
        sub_folders = obj.transparencysubfolder_set.all()
        if not sub_folders:
            return []

        return TransparencySubFolderSerializer(sub_folders, many=True).data


class TransparencySubFolderSerializer(serializers.ModelSerializer):
    reports = serializers.SerializerMethodField()

    class Meta:
        model = TransparencySubFolder
        fields = ["id", "name", "reports"]
        read_only_fields = ["id", "created_by", "created_at"]

    def get_reports(self, obj):
        reports = obj.transparencyreport_set.all()
        if not reports:
            return []

        return TransparencyReportSerializer(reports, many=True).data


class TransparencySchoolSerializer(serializers.ModelSerializer):
    founded_at = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "address",
            "founded_at",
            "contract_expires",
            "gradeserved",
            "contact_phone_number",
            "website_url",
            "logo",
        ]

        read_only_fields = ["id", "created_by", "created_at"]

    def validate_founded_at(self, value):
        if value:
            try:
                # Try to parse as year
                year = int(value)
                current_year = datetime.now().year

                # Validate year is reasonable (not in future and not too far in past)
                if year > current_year:
                    raise serializers.ValidationError(
                        "Founded year cannot be in the future"
                    )
                if year < 1800:  # Reasonable minimum year
                    raise serializers.ValidationError(
                        "Founded year seems too far in the past"
                    )

                # Convert to January 1st of that year
                return datetime(year, 6, 1).date()
            except ValueError:
                raise serializers.ValidationError(
                    "Founded year must be a valid year (e.g., 2020)"
                )
        return value

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%B %d, %Y")

    def save(self, **kwargs):
        return super().save(**kwargs)
