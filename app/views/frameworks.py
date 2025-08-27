from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.frameworks import Framework, FrameworkSection, RateFramework
from app.serializers.frameworks import (
    FrameworkSectionDetailSerializer,
    FrameworkSectionSerializer,
    FrameworkSerializer,
    RateFrameworkDetailSerializer,
    RateFrameworkSerializer,
)
from app.services.base import (
    filterObjects,
    get_paginated_filtered_data,
    process_serializer,
)


class RateFrameworkPKAPI(APIView):
    def get(self, _, pk):
        rateframework = get_object_or_404(RateFramework, pk=pk)
        serializer = RateFrameworkDetailSerializer(rateframework)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        rateframework = get_object_or_404(RateFramework, pk=pk)
        return process_serializer(
            RateFrameworkDetailSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=rateframework,
        )

    def delete(self, _, pk):
        rateframework = get_object_or_404(RateFramework, pk=pk)
        rateframework.delete()
        return Response(
            {"message": MSG_CONST.MSG_NORMAL_DELETE}, status=status.HTTP_204_NO_CONTENT
        )


class RateFrameworkAPI(APIView):

    def get(self, _):
        rate_frameworks = RateFramework.objects.all()
        serializer = RateFrameworkSerializer(rate_frameworks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        return process_serializer(RateFrameworkSerializer, req.data)


class FrameworkAPI(APIView):
    def get(self, _):
        frameworks = Framework.objects.all()
        serializer = FrameworkSerializer(frameworks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        return process_serializer(FrameworkSerializer, req.data)


class FrameworkPKAPI(APIView):
    def get(self, _, pk):
        framework = get_object_or_404(Framework, pk=pk)
        serializer = FrameworkSerializer(framework)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        framework = get_object_or_404(Framework, pk=pk)
        return process_serializer(
            FrameworkSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=framework,
        )

    def delete(self, _, pk):
        framework = get_object_or_404(Framework, pk=pk)
        framework.delete()
        return Response(
            {"message": MSG_CONST.MSG_NORMAL_DELETE}, status=status.HTTP_204_NO_CONTENT
        )


class FrameworkSectionAPI(APIView):
    def get(self, _, framework_pk):
        filter_fields = {"framework_id": framework_pk}
        framework_sections = filterObjects(filter_fields, FrameworkSection)
        serializer = FrameworkSectionSerializer(framework_sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req, framework_pk):
        data = req.data
        data["framework"] = framework_pk
        return process_serializer(FrameworkSectionSerializer, data)


class FrameworkSectionPKAPI(APIView):
    def get(self, _, pk):
        frameworkSection = FrameworkSection.objects.select_related(
            "framework", "rubric"
        ).get(pk=pk)
        serializer = FrameworkSectionDetailSerializer(frameworkSection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        frameworkSection = get_object_or_404(FrameworkSection, pk=pk)
        return process_serializer(
            FrameworkSectionSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=frameworkSection,
        )

    def delete(self, _, pk):
        frameworkSection = get_object_or_404(FrameworkSection, pk=pk)
        frameworkSection.delete()
        return Response(
            {"message": MSG_CONST.MSG_NORMAL_DELETE}, status=status.HTTP_204_NO_CONTENT
        )
