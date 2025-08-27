from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.rubrics import Score
from app.serializers.rubrics import ScoreSerializer
from app.services.base import process_serializer


class RubricScoreAPI(APIView):
    def get(self, _, rubric_pk):
        scores = Score.objects.filter(rubric__id=rubric_pk)
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req, rubric_pk):
        data = req.data
        data["rubric"] = rubric_pk
        return process_serializer(ScoreSerializer, data)


class RubricScorePKAPI(APIView):
    def get(self, _, pk):
        score = get_object_or_404(Score, pk=pk)
        serializer = ScoreSerializer(score)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        score = get_object_or_404(Score, pk=pk)
        return process_serializer(
            ScoreSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=score,
        )

    def delete(self, _, pk):
        score = get_object_or_404(Score, pk=pk)
        score.delete()
        return Response(
            {"message": MSG_CONST.MSG_RUBRIC_SCORE_DELETED}, status.HTTP_204_NO_CONTENT
        )
