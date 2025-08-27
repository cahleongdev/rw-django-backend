from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.applications import (
    Application,
    ApplicationQuestion,
    ApplicationSection,
    ApplicationSubSection,
)
from app.serializers.applications import (
    ApplicationCreateSerializer,
    ApplicationQuestionSerializer,
    ApplicationSectionCreateSerializer,
    ApplicationSectionDetailSerializer,
    ApplicationSectionSerializer,
    ApplicationSectionUpdateSerializer,
    ApplicationSerializer,
    ApplicationSubSectionDetailSerializer,
    ApplicationSubSectionSerializer,
)
from app.services.base import (
    filterObjects,
    get_paginated_filtered_data,
    process_serializer,
)
from app.utils.pagination import CustomPagination


class ApplicationAPI(APIView):
    def get(self, _):
        appliations = Application.objects.all()
        serializer = ApplicationSerializer(appliations, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, req):
        token_data = getattr(req, "token_data", None)
        data = req.data
        data["agency"] = token_data["agency"]
        return process_serializer(ApplicationCreateSerializer, data)


class AgencyAdminApplicationAPI(APIView):
    pagination_class = CustomPagination

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]
        filter_kwargs = {"agency_id": agency}
        return get_paginated_filtered_data(
            req=req,
            model=Application,
            serializer_class=ApplicationSerializer,
            filter_kwargs=filter_kwargs,
            page_size=10,
        )


class ApplicationPKAPI(APIView):
    def get_application(self, _, pk):
        return get_object_or_404(Application, pk=pk)

    def get(self, _, pk):
        application = self.get_application(self, pk)
        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _, pk):
        application = self.get_application(self, pk)
        application.delete()
        return Response(
            {"message": MSG_CONST.MSG_APPLICATION_DELETED},
            status=status.HTTP_204_NO_CONTENT,
        )

    def put(self, req, pk):
        application = self.get_application(self, pk)
        return process_serializer(
            ApplicationSerializer,
            data=req.data,
            success_status=status.HTTP_200_OK,
            original_object=application,
        )


class ApplicationSectionAPI(APIView):
    def get(self, req):
        application_id = req.GET.get("application_pk")
        fields = {"application_id": application_id}
        data = filterObjects(fields, ApplicationSection)
        serializer = ApplicationSectionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        data = req.data
        return process_serializer(ApplicationSectionCreateSerializer, data)


class ApplicationSectionPKAPI(APIView):
    def get(self, _, section_pk):
        applicationSection = get_object_or_404(ApplicationSection, pk=section_pk)
        serializer = ApplicationSectionDetailSerializer(applicationSection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, section_pk):
        applicationSection = get_object_or_404(ApplicationSection, pk=section_pk)
        return process_serializer(
            ApplicationSectionUpdateSerializer,
            data=req.data,
            success_status=status.HTTP_200_OK,
            original_object=applicationSection,
        )

    def delete(self, _, section_pk):
        applicationSection = get_object_or_404(ApplicationSection, pk=section_pk)
        applicationSection.delete()
        return Response(
            {"message": MSG_CONST.MSG_APPLICATION_SECTION_DELETED},
            status=status.HTTP_204_NO_CONTENT,
        )


class ApplicationSubSectionAPI(APIView):
    def get(self, _, section_pk):
        fields = {"application_section_id": section_pk}
        data = filterObjects(fields, ApplicationSubSection)
        serializer = ApplicationSubSectionDetailSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req, section_pk):
        data = req.data
        data["application_section"] = section_pk
        return process_serializer(ApplicationSubSectionSerializer, data)


class ApplicationSubSectionPKAPI(APIView):
    def get(self, _, pk):
        applicationSubSection = get_object_or_404(ApplicationSubSection, pk=pk)
        serializer = ApplicationSubSectionSerializer(applicationSubSection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        applicationSubSection = get_object_or_404(ApplicationSubSection, pk=pk)
        return process_serializer(
            ApplicationSubSectionSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=applicationSubSection,
        )

    def delete(self, _, pk):
        applicationSubSection = get_object_or_404(ApplicationSubSection, pk=pk)
        applicationSubSection.delete()
        return Response(
            {"message": MSG_CONST.MSG_APPLICATION_SUBSECTION_DELETED},
            status=status.HTTP_204_NO_CONTENT,
        )


class ApplicationQuestionAPI(APIView):
    def get(self, _, sub_section_pk):
        fields = {"application_sub_section_id": sub_section_pk}
        data = filterObjects(fields, ApplicationQuestion)
        serializer = ApplicationQuestionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req, sub_section_pk):
        data = req.data
        data["application_sub_section"] = sub_section_pk
        return process_serializer(ApplicationQuestionSerializer, data)


class ApplicationQuestionPKAPI(APIView):
    def get(self, _, pk):
        applicationQuestion = get_object_or_404(ApplicationQuestion, pk=pk)
        serializer = ApplicationQuestionSerializer(applicationQuestion)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        applicationQuestion = get_object_or_404(ApplicationQuestion, pk=pk)
        return process_serializer(
            ApplicationQuestionSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=applicationQuestion,
        )

    def delete(self, _, pk):
        applicationQuestion = get_object_or_404(ApplicationQuestion, pk=pk)
        applicationQuestion.delete()
        return Response(
            {"message": MSG_CONST.MSG_APPLICATION_QUESTION_DELETED},
            status=status.HTTP_204_NO_CONTENT,
        )
