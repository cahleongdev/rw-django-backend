from datetime import datetime
from django.db import transaction
from django.db.models import Prefetch

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.enumeration import UserRole
from app.models.agencies import Agency
from app.models.transparency import (
    TransparencyDetail,
    TransparencyFolder,
    TransparencySubFolder,
    TransparencyReport,
)
from app.models.users import User
from app.serializers.transparency import (
    TransparencyDetailsSerializer,
    TransparencyFolderSerializer,
    TransparencySubFolderSerializer,
    TransparencyReportSerializer,
    TransparencySchoolSerializer,
)
from app.services.base import process_serializer
from app.utils.helper import generateUniqueID
from app.models.schools import School
from django.shortcuts import get_object_or_404


class TransparencyDetailsAPI(APIView):
    def get(self, req, pk=None):
        try:
            if pk:
                agency = get_object_or_404(Agency, pk=pk)
            else:
                agency = req.query_params.get("agency_id")

            transparency = TransparencyDetail.objects.filter(agency=agency).first()

            serializer = TransparencyDetailsSerializer(transparency)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Error getting transparency details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)
            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            transparency_detail_query = TransparencyDetail.objects.filter(
                agency=current_user.agency
            )

            if transparency_detail_query.exists():
                transparency_detail = transparency_detail_query.first()
                return process_serializer(
                    TransparencyDetailsSerializer,
                    req.data,
                    updated_by=current_user,
                    success_status=status.HTTP_200_OK,
                    original_object=transparency_detail,
                )

            return process_serializer(
                TransparencyDetailsSerializer,
                req.data,
                agency=current_user.agency,
                updated_by=current_user,
                success_status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Error updating transparency details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransparencyFolderAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            if not token_data:
                current_agency = Agency.objects.get(
                    id=req.query_params.get("agency_id")
                )
            else:
                current_user = User.objects.get(
                    id=token_data["user_id"], deleted_at=None
                )
                current_agency = current_user.agency

            folders = (
                TransparencyFolder.objects.filter(agency=current_agency)
                .select_related("agency")
                .prefetch_related(
                    Prefetch(
                        "transparencysubfolder_set",
                        queryset=TransparencySubFolder.objects.select_related(
                            "reports"
                        ).prefetch_related(
                            Prefetch(
                                "transparencyreport_set",
                                queryset=TransparencyReport.objects.select_related(
                                    "report"
                                ),
                            )
                        ),
                    )
                )
            )

            serializer = TransparencyFolderSerializer(folders, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Error creating room"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)

            # Check if user is an agency admin
            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return process_serializer(
                TransparencyFolderSerializer,
                req.data,
                agency=current_user.agency,
                created_by=current_user,
                updated_by=current_user,
                success_status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": "Error creating folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, req, pk):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)

            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            transparency_folder = get_object_or_404(TransparencyFolder, pk=pk)

            return process_serializer(
                TransparencyFolderSerializer,
                req.data,
                updated_by=current_user,
                original_object=transparency_folder,
                success_status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Error updating folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, req, pk):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )

            current_user_role = UserRole(current_user.role)

            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            folder = get_object_or_404(TransparencyFolder, pk=pk)

            folder.delete()

            return Response("Folder deleted successfully")

        except Exception as e:
            return Response(
                {"error": "Error deleting folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransparencyReportAPI(APIView):
    def post(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)

            sub_folder_id = req.data.get("sub_folder_id")
            report_ids = req.data.get("report_ids")

            if current_user_role != UserRole.AGENCY_ADMIN or not sub_folder_id:
                return Response(
                    {
                        "error": "User is not an agency admin or sub folder id is required"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            with transaction.atomic():
                sub_folder = get_object_or_404(TransparencySubFolder, pk=sub_folder_id)

                existing_reports = TransparencyReport.objects.filter(
                    sub_folder=sub_folder
                ).values_list("id", flat=True)

                reports_to_remove = set(existing_reports) - set(report_ids)

                if reports_to_remove:
                    TransparencyReport.objects.filter(
                        sub_folder=sub_folder, id__in=reports_to_remove
                    ).delete()

                new_reports = set(req.data["report_ids"]) - set(existing_reports)

                if new_reports:
                    TransparencyReport.objects.bulk_create(
                        [
                            TransparencyReport(
                                id=generateUniqueID(),
                                sub_folder=sub_folder,
                                report_id=report_id,
                            )
                            for report_id in new_reports
                        ]
                    )

                all_sub_folder_reports = TransparencyReport.objects.filter(
                    sub_folder=sub_folder
                ).select_related("report")

                serializer = TransparencyReportSerializer(
                    all_sub_folder_reports,
                    many=True,
                )

                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Error creating report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransparencySubFolderAPI(APIView):
    def post(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)

            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return process_serializer(
                TransparencySubFolderSerializer,
                req.data,
                folder_id=req.data["folder_id"],
                created_by=current_user,
                updated_by=current_user,
                success_status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": "Error creating sub folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, req, pk):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)
            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            transparency_sub_folder = get_object_or_404(TransparencySubFolder, pk=pk)

            return process_serializer(
                TransparencySubFolderSerializer,
                req.data,
                updated_by=current_user,
                original_object=transparency_sub_folder,
                success_status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Error updating sub folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, req, pk):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )

            current_user_role = UserRole(current_user.role)

            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            sub_folder = get_object_or_404(TransparencySubFolder, pk=pk)
            sub_folder.delete()
            return Response("Sub folder deleted successfully")

        except Exception as e:
            return Response(
                {"error": "Error deleting sub folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransparencySchoolsAPI(APIView):
    def get(self, _, pk):
        try:
            agency = get_object_or_404(Agency, pk=pk)

            schools = School.objects.filter(agency=agency).exclude(type="Network")

            serializer = TransparencySchoolSerializer(schools, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Error getting transparency details"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, req, pk):
        try:
            token_data = getattr(req, "token_data", None)
            current_user = User.objects.get(
                id=token_data["user_id"], deleted_at=None
            )
            current_user_role = UserRole(current_user.role)

            if current_user_role != UserRole.AGENCY_ADMIN:
                return Response(
                    {"error": "User is not an agency admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            school = get_object_or_404(School, pk=pk)

            return process_serializer(
                TransparencySchoolSerializer,
                req.data,
                updated_by=current_user,
                success_status=status.HTTP_200_OK,
                original_object=school,
            )

        except Exception as e:
            return Response(
                {"error": "Error creating transparency schools"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
