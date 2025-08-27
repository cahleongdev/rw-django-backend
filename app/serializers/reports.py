from django.db import models
from rest_framework import serializers

from app.models.report_schedules import ReportSchedule
from app.models.report_scoring import ReportScoring
from app.models.reports import Report, ReportCategory
from app.models.submissions import Submission
from app.models.submission_instructions import SubmissionInstruction
from app.serializers.report_schedules import ReportScheduleSerializer
from app.serializers.report_scoring import ReportScoringSerializer
from app.serializers.submission_instructions import SubmissionInstructionSerializer
from app.serializers.users import UserFullNameSerializer
from app.models.agencies import Agency


class ReportSerializer(serializers.ModelSerializer):
    # Explicitly define categories field to handle array of IDs
    name = serializers.CharField(required=True, allow_null=False)
    categories = serializers.PrimaryKeyRelatedField(
        many=True,  # This makes it handle arrays
        queryset=ReportCategory.objects.all(),
        required=False,
    )
    schedules = ReportScheduleSerializer(many=True, required=False)
    submission_instruction = SubmissionInstructionSerializer(
        required=False, allow_null=True
    )
    scoring = ReportScoringSerializer(required=False, allow_null=True)
    has_scoring = serializers.SerializerMethodField()
    edited_by = UserFullNameSerializer(read_only=True)
    assigned_schools = serializers.SerializerMethodField()

    # Custom field to handle null values for schedule_type
    schedule_type = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["id", "edited_by"]

    def validate_schedule_type(self, value):
        """
        Handle null schedule_type values by converting to model default
        """
        if value is None:
            return "SPECIFIC_DATES"  # Model default
        return value

    def validate(self, data):
        """
        Validate recurring schedule data
        """
        # Use model default if schedule_type is not provided
        schedule_type = data.get("schedule_type", "SPECIFIC_DATES")

        if schedule_type == "RECURRING_DATES":
            # Check if all required recurring fields are present
            recurring_fields = [
                "recurring_period",
                "recurring_interval",
                "recurring_occurrences",
                "recurring_first_occurrence",
            ]
            missing_fields = [
                field for field in recurring_fields if not data.get(field)
            ]
            if missing_fields:
                raise serializers.ValidationError(
                    f"Missing required recurring schedule fields: {', '.join(missing_fields)}"
                )

            # Validate interval is positive
            if data.get("recurring_interval", 0) <= 0:
                raise serializers.ValidationError(
                    "Recurring interval must be a positive number"
                )

            # Validate occurrences is positive
            if data.get("recurring_occurrences", 0) <= 0:
                raise serializers.ValidationError(
                    "Recurring occurrences must be a positive number"
                )

        return data

    def create(self, validated_data):
        categories_data = validated_data.pop("categories", [])
        schedules_data = validated_data.pop("schedules", [])
        scoring_data = validated_data.pop("scoring", None)
        instruction_data = validated_data.pop("submission_instruction", None)

        # Create the report first
        report = Report.objects.create(**validated_data)

        # Add categories if any
        if categories_data:
            report.categories.set(categories_data)

        # Create schedules
        for schedule_data in schedules_data:
            if schedule_data:  # Only create if schedule_data is not empty
                ReportSchedule.objects.create(report=report, **schedule_data)

        # Create scoring if provided and not None
        if scoring_data is not None and scoring_data:
            ReportScoring.objects.create(report=report, **scoring_data)

        # Create submission instruction if provided
        if instruction_data and instruction_data:
            SubmissionInstruction.objects.create(report=report, **instruction_data)

        return report

    def update(self, instance, validated_data):
        categories_data = validated_data.pop("categories", None)
        schedules_data = validated_data.pop("schedules", None)
        scoring_data = validated_data.pop("scoring", None)
        instruction_data = validated_data.pop("submission_instruction", None)

        # Update categories if provided
        if categories_data is not None:
            instance.categories.set(categories_data)

        # Update schedules if provided
        if schedules_data is not None:
            if validated_data.get("schedule_type") != instance.schedule_type:
                instance.schedules.all().delete()

                for schedule_data in schedules_data:
                    if schedule_data:  # Only create if schedule_data is not empty
                        ReportSchedule.objects.create(report=instance, **schedule_data)

            else:
                all_schedules = instance.schedules.all()

                current_schedules = instance.schedules.filter(
                    schedule_time__in=[
                        date.get("schedule_time")
                        for date in schedules_data
                        if date and date.get("schedule_time")
                    ]
                )

                remove = all_schedules.exclude(
                    id__in=[schedule.id for schedule in current_schedules]
                )

                remove.delete()

                # For the new schedules data, we should overwrite the name
                for schedule_data in schedules_data:
                    if schedule_data and schedule_data.get(
                        "schedule_time"
                    ):  # Only process if schedule_data is not empty and has schedule_time
                        ReportSchedule.objects.update_or_create(
                            report=instance,
                            schedule_time=schedule_data.get("schedule_time"),
                            defaults={"report_name": schedule_data.get("report_name")},
                        )

        # Update scoring if provided
        if scoring_data is not None and scoring_data:
            if hasattr(instance, "scoring"):
                # Update existing scoring
                for key, value in scoring_data.items():
                    setattr(instance.scoring, key, value)
                instance.scoring.save()
            else:
                # Create new scoring
                ReportScoring.objects.create(report=instance, **scoring_data)

        # Update submission instruction if provided
        if instruction_data is not None and instruction_data:
            if hasattr(instance, "submission_instruction"):
                for key, value in instruction_data.items():
                    setattr(instance.submission_instruction, key, value)
                instance.submission_instruction.save()
            else:
                SubmissionInstruction.objects.create(
                    report=instance, **instruction_data
                )
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_has_scoring(self, obj):
        """Check if report has scoring criteria set up"""
        return obj.use_scoring and hasattr(obj, "scoring")

    def get_assigned_schools(self, obj):
        """Get list of assigned schools with details"""
        return list(
            Submission.objects.filter(report_schedule__report=obj)
            .select_related("school")  # Optimize by fetching school data in same query
            .values("school_id", "school__name")
            .annotate(
                id=models.F("school_id"),
                name=models.F("school__name"),
                assigned_at=models.F("created_at"),
            )
            .values("id", "name", "assigned_at")
        )


class ReportListSerializer(serializers.ModelSerializer):
    assigned_schools = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "name",
            "report",
            "domain",
            "due_date",
            "use_scoring",
            "schedule_type",
            "recurring_period",
            "recurring_interval",
            "recurring_occurrences",
            "recurring_first_occurrence",
            "approved",
            "assigned_schools",
        ]

    def get_assigned_schools(self, obj):
        """Get list of assigned schools with details"""
        return list(
            Submission.objects.filter(report=obj)
            .select_related("school")
            .values("school_id", "school__name")
            .annotate(
                id=models.F("school_id"),
                name=models.F("school__name"),
                assigned_at=models.F("created_at"),
            )
            .values("id", "name", "assigned_at")
        )


class ReportCategorySerializer(serializers.ModelSerializer):
    agency_id = serializers.PrimaryKeyRelatedField(
        source="agency", queryset=Agency.objects.all(), required=False
    )

    class Meta:
        model = ReportCategory
        fields = ["id", "name", "color", "agency_id"]
        read_only_fields = ["id"]


class ReportDetailSerializer(serializers.ModelSerializer):
    categories = ReportCategorySerializer(many=True, read_only=True)
    schedule_times = serializers.SerializerMethodField()
    edited_by = UserFullNameSerializer(read_only=True)
    assigned_schools = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "name",
            "categories",
            "schedule_times",
            "edited_by",
            "approved",
            "assigned_schools",
        ]

    def get_schedule_times(self, obj):
        """Get all schedule times for this report"""
        schedules = obj.schedules.all().order_by("schedule_time")
        return [
            {
                "id": schedule.id,
                "schedule_time": schedule.schedule_time,
                "report_name": schedule.report_name,
            }
            for schedule in schedules
        ]

    def get_assigned_schools(self, obj):
        """Get list of assigned schools with details"""
        return list(
            Submission.objects.filter(report=obj)
            .select_related("school")
            .values("school_id", "school__name")
            .annotate(
                id=models.F("school_id"),
                name=models.F("school__name"),
                assigned_at=models.F("created_at"),
            )
            .values("id", "name", "assigned_at")
        )


class SubmissionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id",
            "name",
            "report",
            "domain",
            "due_date",
        ]
