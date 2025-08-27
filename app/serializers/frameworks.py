from rest_framework import serializers

from app.models.frameworks import Framework, FrameworkSection, RateFramework
from app.serializers.rubrics import RubricSerializer
from app.serializers.schools import SchoolSerializer


class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = ["id", "title", "description"]


class FrameworkSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameworkSection
        fields = ["id", "framework", "title", "description", "rubric", "score_types"]


class FrameworkSectionDetailSerializer(serializers.ModelSerializer):
    framework = FrameworkSerializer(read_only=True)
    rubric = RubricSerializer(read_only=True)

    class Meta:
        model = FrameworkSection
        fields = ["id", "framework", "title", "description", "rubric", "score_types"]


class RateFrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateFramework
        fields = ["id", "school", "framework", "status"]


class RateFrameworkDetailSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    framework = FrameworkSerializer(read_only=True)

    class Meta:
        model = RateFramework
        fields = ["id", "school", "framework", "status"]
