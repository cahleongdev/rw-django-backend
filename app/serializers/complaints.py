from rest_framework import serializers

from app.models.complaints import Complaint
from app.serializers.schools import SchoolNameSerializer
from app.serializers.users import UserNameSerializer


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "id",
            "first_name",
            "last_name",
            "description",
            "agency",
            "school",
            "status",
            "phone_number",
            "opened_date",
            "resolved_date",
            "assigned_member",
        ]


class ComplaintListSerializer(serializers.ModelSerializer):
    school = SchoolNameSerializer(read_only=True)
    assigned_member = UserNameSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "id",
            "first_name",
            "last_name",
            "description",
            "agency",
            "school",
            "status",
            "phone_number",
            "opened_date",
            "resolved_date",
            "assigned_member",
        ]
