from rest_framework import serializers

from app.models.submissions import Submission


class DashboardsSubmittedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "due_date",
            "status",
            "assigned_member",
            "evaluator",
            "school_submission_date",
            "evaluator_submission_date",
            "school_submission_explanation",
            "file_urls",
        ]
