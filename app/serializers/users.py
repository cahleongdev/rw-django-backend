from rest_framework import serializers

from app.models.users import User

from app.enumeration.mfa import MFAMethod


class SchoolAssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "title",
            "role",
            "is_active",
        ]


class MessageUserSerializer(serializers.ModelSerializer):
    schools = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "title",
            "role",
            "is_active",
            "schools",
            "agency",
            "role",
        ]

    def get_schools(self, obj):
        return [
            {"id": school.id, "name": school.name}
            for school in obj.schools.only("id", "name")
        ]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label="Confirm Password")
    mfa_method = serializers.ListField(
        child=serializers.ChoiceField(choices=MFAMethod.choices()),
        required=False,
        allow_empty=True,
    )
    title = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "profile_image",
            "role",
            "title",
            "is_active",
            "date_joined",
            "schools",
            "agency",
            "custom_fields",
            "permissions",
            "notification_settings",
            "mfa_method",
            "mfa_enabled",
            "password",
            "password2",
        ]


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name"]


class UserFullNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class UserNotifcationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "notification_settings"]
