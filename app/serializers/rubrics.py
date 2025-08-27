from rest_framework import serializers

from app.models.rubrics import Rubric, Score


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ["id", "title", "description", "score", "rubric", "color"]


class RubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubric
        fields = ["id", "title", "description"]


class RubricWithScoreSerializer(serializers.ModelSerializer):
    scores = ScoreSerializer(many=True, read_only=True, source="score_set")

    class Meta:
        model = Rubric
        fields = ["id", "title", "description", "scores"]
