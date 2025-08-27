from rest_framework import serializers

from app.models.submissions import Submission, SubmissionMessage
from app.serializers.reports import ReportSerializer, SubmissionReportSerializer
from app.serializers.schools import (
    SchoolNameSerializer,
    SchoolSerializer,
    SubmissionSchoolSerializer,
)
from app.serializers.users import UserFullNameSerializer, UserSerializer


class SubmissionSerializer(serializers.ModelSerializer):
    report = ReportSerializer(source="report_schedule.report", read_only=True)
    school = SchoolSerializer(read_only=True)
    assigned_member = UserSerializer(read_only=True)
    due_date = serializers.DateTimeField(source="report_schedule.schedule_time")

    class Meta:
        model = Submission
        fields = [
            "id",
            "agency",
            "due_date",
            "report",
            "school",
            "status",
            "assigned_member",
            "evaluator",
            "submission_content",
            "school_submission_date",
            "evaluator_submission_date",
            "school_submission_explanation",
            "file_urls",
        ]


class SubmissionCreateAndUpdateSerializer(serializers.ModelSerializer):
    due_date = serializers.DateTimeField(source="report_schedule.schedule_time")
    report = serializers.CharField(source="report_schedule.report.id")

    class Meta:
        model = Submission
        fields = [
            "id",
            "agency",
            "due_date",
            "report",
            "report_schedule",
            "school",
            "status",
            "submission_content",
            "assigned_member",
            "evaluator",
            "school_submission_date",
            "evaluator_submission_date",
            "school_submission_explanation",
            "file_urls",
            "created_by",
            "updated_by",
        ]

    def update(self, instance, validated_data):
        # Handle dotted source fields separately
        report_schedule = validated_data.pop("report_schedule", None)

        # Update the report_schedule if due_date or report_id is provided
        if report_schedule is not None:
            if instance.report_schedule:
                # Update existing report_schedule
                if report_schedule.get("schedule_time") is not None:
                    instance.report_schedule.schedule_time = report_schedule.get(
                        "schedule_time"
                    )

                instance.report_schedule.save()

        # Update other fields normally
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class SubmissionSchoolDetailSerializer(serializers.ModelSerializer):
    report = SubmissionReportSerializer(read_only=True)
    assigned_member = UserFullNameSerializer(read_only=True)
    due_date = serializers.DateTimeField(source="report_schedule.schedule_time")

    class Meta:
        model = Submission
        fields = [
            "id",
            "agency",
            "due_date",
            "report",
            "status",
            "assigned_member",
            "evaluator",
            "school_submission_date",
            "evaluator_submission_date",
            "school_submission_explanation",
            "file_urls",
        ]


class SubmissionFilterBySchoolSerializer(serializers.ModelSerializer):
    report = SubmissionReportSerializer(read_only=True)
    due_date = serializers.DateTimeField(source="report_schedule.schedule_time")

    class Meta:
        model = Submission
        fields = [
            "id",
            "due_date",
            "report",
            "status",
            "assigned_member",
            "school_submission_date",
            "evaluator_submission_date",
        ]


class SubmissionFilterByReportSerializer(serializers.ModelSerializer):
    school = SubmissionSchoolSerializer(read_only=True)
    due_date = serializers.DateTimeField(source="report_schedule.schedule_time")

    class Meta:
        model = Submission
        fields = [
            "id",
            "due_date",
            "school",
            "status",
            "assigned_member",
            "school_submission_date",
            "evaluator_submission_date",
        ]


class SubmissionMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionMessage
        fields = ["id", "sender", "content", "submission", "created_at"]


class SubmissionMessageDetailSerializer(serializers.ModelSerializer):
    sender = UserFullNameSerializer(read_only=True)

    class Meta:
        model = SubmissionMessage
        fields = ["id", "sender", "content", "submission", "created_at"]


class SchoolSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["school", "report"]


class SchoolSubmissionSerializer(serializers.ModelSerializer):
    school = SchoolNameSerializer(read_only=True)
    report = ReportSerializer(source="report_schedule.report", read_only=True)

    class Meta:
        model = Submission
        fields = ["id", "school", "report", "status"]
