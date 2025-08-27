from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.rubrics import Rubric
from app.serializers.rubrics import RubricSerializer, RubricWithScoreSerializer
from app.services.base import process_serializer


class RubricAPI(APIView):
    def get(self, _):
        data = Rubric.objects.all()
        serializer = RubricWithScoreSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        return process_serializer(RubricSerializer, req.data)


class RubricPKAPI(APIView):
    def get(self, _, pk):
        try:
            rubric = Rubric.objects.prefetch_related("score_set").get(id=pk)
        except Rubric.DoesNotExist:
            return Response(
                {"error": MSG_CONST.MSG_RUBRIC_VALIDATION["error"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RubricWithScoreSerializer(rubric)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        rubric = get_object_or_404(Rubric, pk=pk)
        return process_serializer(
            RubricSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=rubric,
        )

    def delete(self, _, pk):
        rubric = get_object_or_404(Rubric, pk=pk)
        rubric.delete()
        return Response(
            {"message": MSG_CONST.MSG_RUBRIC_DELETED}, status=status.HTTP_200_OK
        )
