from rest_framework import serializers

from app.models.report_activities import ReportActivity
from app.serializers.users import UserFullNameSerializer


class ReportActivitySerializer(serializers.ModelSerializer):
    user = UserFullNameSerializer(read_only=True)

    class Meta:
        model = ReportActivity
        fields = ["id", "report", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
