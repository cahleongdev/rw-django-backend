from rest_framework import serializers

from app.models.report_schedules import ReportSchedule


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = ["id", "schedule_time", "report_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportScheduleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = ["id", "schedule_time", "report_name"]
        read_only_fields = ["id"]
