from rest_framework import serializers

from app.models.applications import (
    ApplicationComment,
    ApplicationMessage,
    ApplicationSchool,
    ApplicationSchoolSection,
    ApplicationSchoolSubSection,
)
from app.serializers.applications import ApplicationSerializer
from app.serializers.schools import SchoolNameSerializer


class ApplicationSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSchool
        fields = [
            "id",
            "application",
            "school",
            "submission_time",
            "due_date",
            # "application_school_section_list",
        ]


class ApplicationSchoolListSerializer(serializers.ModelSerializer):
    school = SchoolNameSerializer

    class Meta:
        model = ApplicationSchool
        fields = [
            "id",
            "application",
            "school",
            "submission_time",
            "due_date",
        ]


class ApplicationSchoolDetailSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    school = SchoolNameSerializer(read_only=True)

    class Meta:
        model = ApplicationSchool
        fields = [
            "id",
            "application",
            "school",
            "submission_time",
            "due_date",
            # "application_school_section_list",
        ]


class ApplicationNameSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)

    class Meta:
        model = ApplicationSchool
        fields = [
            "id",
            "application",
            "school",
            "submission_time",
            "due_date",
        ]


class ApplicationSchoolSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSchoolSection
        fields = [
            "id",
            "application_school",
            "application_school_section",
            "grad",
            "assigned_member",
        ]


class ApplicationSchoolSubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSchoolSubSection
        fields = [
            "id",
            "application_school",
            "application_school_sub_section",
            "grad",
            "assigned_member",
            "answers",
        ]


class ApplicationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationMessage
        fields = ["id", "sender", "application_school", "content"]


class ApplicationCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationComment
        fields = ["id", "sender", "content"]


class ApplicationCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationComment
        fields = [
            "id",
            "sender",
            "content",
            "application_school",
            "application_school_section",
            "application_school_sub_section",
        ]
