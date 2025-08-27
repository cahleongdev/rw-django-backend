from rest_framework import serializers

from app.models.applications import (
    Application,
    ApplicationQuestion,
    ApplicationSection,
    ApplicationSubSection,
)
from app.serializers.rubrics import RubricWithScoreSerializer
from app.serializers.users import UserNameSerializer


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "name",
            "due_date",
            "description",
            "agency",
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "name",
            "due_date",
            "description",
        ]


class ApplicationSectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSection
        fields = ["id", "application", "title", "description", "user", "rubric"]
        extra_kwargs = {
            "application": {"required": True},
        }


class ApplicationSectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSection
        fields = ["id", "title", "description", "user", "rubric"]


class ApplicationSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSection
        fields = ["id", "title", "description", "user", "rubric"]


class ApplicationSectionDetailSerializer(serializers.ModelSerializer):
    user = UserNameSerializer(read_only=True)
    rubric = RubricWithScoreSerializer(read_only=True)

    class Meta:
        model = ApplicationSection
        fields = ["id", "title", "description", "user", "rubric"]


class ApplicationSubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSubSection
        fields = ["id", "title", "description", "user", "rubric", "application_section"]


class ApplicationSubSectionDetailSerializer(serializers.ModelSerializer):
    user = UserNameSerializer(read_only=True)
    rubric = RubricWithScoreSerializer(read_only=True)

    class Meta:
        model = ApplicationSubSection
        fields = ["id", "title", "description", "user", "rubric"]


class ApplicationQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationQuestion
        fields = ["id", "type", "content", "application_sub_section"]
