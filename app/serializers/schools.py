from rest_framework import serializers

from app.models.schools import School
from app.serializers.agencies import AgencySchoolPrivilegeSerializer
from app.serializers.users import SchoolAssignedUserSerializer

from app.enumeration.user_role import UserRole

class SchoolSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    agency = AgencySchoolPrivilegeSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "address",
            "city",
            "state",
            "zipcode",
            "county",
            "district",
            "type",
            "gradeserved",
            "custom_fields",
            "network",
            "agency",
            "users",
            "status",
            "board_meetings",
        ]
        extra_kwargs = {
            "gradeserved": {"required": False},
            "county": {"required": False},
            "state": {"required": False},
            "zipcode": {"required": False},
            "address": {"required": False},
            "district": {"required": False},
            "network": {"required": False},
        }

    def get_users(self, obj):
        active_users = obj.users.filter(deleted_at__isnull=True)
        return SchoolAssignedUserSerializer(active_users, many=True).data
    
    def get_status(self, obj):
        has_admin = obj.users.filter(
            role=UserRole.SCHOOL_ADMIN.value, 
            deleted_at__isnull=True
        ).exists()
        return "Active" if has_admin else "Inactive"


class ListSchoolWithUserSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    schools = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "address",
            "city",
            "state",
            "zipcode",
            "county",
            "district",
            "type",
            "gradeserved",
            "custom_fields",
            "board_meetings",
            "network",
            "users",
            "status",
            "schools",
        ]

    def get_users(self, obj):
        active_users = obj.users.filter(deleted_at__isnull=True)
        return SchoolAssignedUserSerializer(active_users, many=True).data

    def get_schools(self, obj):
        if obj.type != "Network":
            return None
        network_schools = School.objects.filter(network=obj)
        return SchoolSerializer(network_schools, many=True).data
    
    def get_status(self, obj):
        has_admin = obj.users.filter(
            role=UserRole.SCHOOL_ADMIN.value, 
            deleted_at__isnull=True
        ).exists()
        return "Active" if has_admin else "Inactive"

class SchoolNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name"]


class SchoolDetailWithAgencySerializer(serializers.ModelSerializer):
    agency = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "gradeserved",
            "county",
            "type",
            "state",
            "zipcode",
            "address",
            "district",
            "agency",
            "city",
        ]


class SubmissionSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "gradeserved"]
