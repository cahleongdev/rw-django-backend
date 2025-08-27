from rest_framework import serializers

from app.models.report_scoring import ReportScoring


class ReportScoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportScoring
        fields = [
            "id",
            "exceed",
            "meet",
            "approach",
            "notmeet",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
