from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

import app.constants.msg as MSG_CONST
from app.enumeration import NotificationType
from app.enumeration.user_role import UserRole
from app.models.notifications import Notification
from app.models.schools import School
from app.models.board_members import BoardMember
from app.models.submissions import Submission
from app.models.users import User
from app.serializers.schools import (
    ListSchoolWithUserSerializer,
    SchoolDetailWithAgencySerializer,
    SchoolSerializer,
)
from app.serializers.users import UserSerializer
from app.serializers.board_members import BoardMemberDetailSerializer
from app.serializers.submissions import SchoolSubmissionSerializer
from app.services.base import filterObjects, process_serializer
from app.services.school_reports import addSchoolToReport, deleteSchoolFromReport
from app.services.users import generate_token_code, send_invitation_email
from app.utils.helper import generateUniqueID
from app.utils.pagination import CustomPagination
from app.views.notifications import notification_service

ENTITY_MODEL_MAP = {
    "Schools": School,
    "Networks": School,
    "Users": User,
    "Board Members": BoardMember,
}

SERIALIZER_MAP = {
    "Schools": SchoolSerializer,
    "Networks": SchoolSerializer,
    "Users": UserSerializer,
    "Board Members": BoardMemberDetailSerializer,
}


class SchoolAPI(APIView):
    def get(self, req):
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]
        fields = {"agency": agency}
        schools = filterObjects(fields, School)
        serializer = ListSchoolWithUserSerializer(schools, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        token_data = getattr(req, "token_data", None)
        return process_serializer(
            SchoolSerializer, req.data, agency_id=token_data["agency"]
        )


class SchoolPKAPI(APIView):
    def get_school(self, _, pk):
        return get_object_or_404(School, pk=pk)

    def get_school_user(self, _, pk):
        return School.objects.prefetch_related("school_users__user").get(pk=pk)

    def get(self, _, pk):
        school = self.get_school(self, pk)
        serializer = SchoolSerializer(school, read_only=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _, pk):
        school = self.get_school(self, pk)
        school.delete()
        return Response(
            {"message": MSG_CONST.MSG_SCHOOL_DELETED}, status=status.HTTP_204_NO_CONTENT
        )

    def put(self, req, pk):
        school = self.get_school(self, pk)
        serializer = SchoolSerializer(school, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Create notifications all users at the school
            notifications = []
            if req.data.get("board_meetings"):

                new_notifications = [
                    Notification(
                        id=generateUniqueID(),
                        description=f"Board meeting updated: {serializer.data.get('name')}",
                        type=NotificationType.BOARD_CALENDAR_UPDATE,
                        receiver_id=user.id,
                        school_ids=[pk],
                        created_at=datetime.now(),
                    )
                    for user in User.objects.filter(
                        schools__id=pk, deleted_at=None
                    )
                ]

                notifications.extend(new_notifications)

            if any(
                key in req.data.keys()
                for key in [
                    "name",
                    "address",
                    "city",
                    "state",
                    "zipcode",
                    "gradeserved",
                    "county",
                    "district",
                    "type",
                ]
            ):
                # School info update
                new_notifications = [
                    Notification(
                        id=generateUniqueID(),
                        description=f"School updated: {serializer.data.get('name')}",
                        type=NotificationType.SCHOOL_INFO_UPDATE,
                        receiver_id=user.id,
                        school_ids=[pk],
                        created_at=datetime.now(),
                    )
                    for user in User.objects.filter(
                        schools__id=pk, deleted_at=None
                    )
                ]

                notifications.extend(new_notifications)

            if notifications:
                notification_service.create_notifications(
                    notifications=notifications,
                    create_batch=True,
                )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolDetailWithAgencyAPI(APIView):
    def get(req, pk):
        school = School.objects.prefetch_related("agency").get(pk=pk)
        serializer = SchoolDetailWithAgencySerializer(school)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgencyAdminSchoolAPI(ListAPIView):
    pagination_class = CustomPagination

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        queryset = School.objects.filter(
            agency_id=token_data["agency"], network__isnull=True
        ).order_by("-created_at")
        serializer = ListSchoolWithUserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SchoolSubmissionAPI(APIView):
    def get(self, req, pk):
        queryset = Submission.objects.filter(school_id=pk)
        serializer = SchoolSubmissionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req, pk):
        report_ids = req.data.get("reports", [])
        return addSchoolToReport(pk, report_ids)


class SchoolSubmissionDeleteAPI(APIView):
    def post(self, req, pk):
        school_id = pk
        report_id = req.data.get("report")

        return deleteSchoolFromReport(school_id=school_id, report_id=report_id)


class SchoolBulkImportAPI(APIView):
    def post(self, request):
        entity = request.data.get("entity")
        data = request.data.get("data", [])
        token_data = getattr(request, "token_data", None)

        if not entity or entity not in ENTITY_MODEL_MAP or entity not in SERIALIZER_MAP:
            return Response(
                {"message": "Invalid entity type."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(data, list) or not data:
            return Response(
                {"message": "No data provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        Model = ENTITY_MODEL_MAP[entity]
        Serializer = SERIALIZER_MAP[entity]
        errors = []
        created_ids = []

        try:
            with transaction.atomic():
                for idx, item in enumerate(data):
                    static_fields = item.get("staticFields", {})
                    custom_fields = item.get("customFields", {})

                    model_fields = {**static_fields}
                    if hasattr(Model, "custom_fields"):
                        model_fields["custom_fields"] = custom_fields

                    model_fields["agency"] = token_data.get("agency", None)

                    # gradeserved as list for Schools
                    if entity == "Schools" and "gradeserved" in model_fields:
                        gradeserved = model_fields["gradeserved"]
                        if isinstance(gradeserved, str):
                            model_fields["gradeserved"] = [
                                g.strip() for g in gradeserved.split(",") if g.strip()
                            ]

                    # type as Network to identify in Schools
                    if entity == "Networks":
                        model_fields["type"] = "Network"

                    # agency_id for Users
                    if entity == "Users":
                        model_fields["is_active"] = False

                    serializer = Serializer(data=model_fields, partial=True)
                    if serializer.is_valid():
                        obj = serializer.save()
                        created_ids.append(obj.id)

                        if entity == "Users":
                            # send invitation email
                            inviting_user = request.user
                            token = generate_token_code(obj, inviting_user)
                            send_invitation_email(request, obj, inviting_user, token)
                    else:
                        errors.append({"row": idx + 1, "error": serializer.errors})

                if errors:
                    # If any error, rollback the transaction
                    raise Exception("Validation error in import")

        except Exception:
            return Response(
                {
                    "created_count": 0,
                    "errors": errors or "Bulk import failed. No records created.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "created_count": len(created_ids),
                "errors": [],
            },
            status=status.HTTP_201_CREATED,
        )
