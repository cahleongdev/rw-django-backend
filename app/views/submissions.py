from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
import boto3
from django.conf import settings
from urllib.parse import urlparse

import app.constants.msg as MSG_CONST
from app.enumeration import NotificationType, SubmissionStatus, UserRole

from app.models.agencies import Agency
from app.models.notifications import Notification
from app.models.reports import Report
from app.models.submissions import Submission, SubmissionMessage
from app.models.users import User
from app.models.schools import School
from app.serializers.submissions import (
    SubmissionCreateAndUpdateSerializer,
    SubmissionMessageDetailSerializer,
    SubmissionMessageSerializer,
    SubmissionSchoolDetailSerializer,
    SubmissionSerializer,
)
from app.services.base import filterObjects, process_serializer
from app.services.files import generate_get_presigned_url
from app.services.reports import get_reports_with_multiple_submissions
from app.services.school_reports import filterSchoolReports
from app.services.schools import get_schools_with_multiple_submissions
from app.views.notifications import notification_service
from app.utils.helper import generateUniqueID
from app.services.aws_mock import mock_aws_service
from app.utils.pagination import CustomPagination


class SubmissionAPI(APIView):

    def get(self, req):
        fields = {
            "report_id": req.GET.get("report"),
            "school_id": req.GET.get("school"),
            "due_date": req.GET.get("due_date"),
        }
        data = filterObjects(fields, Submission)
        serializer = SubmissionCreateAndUpdateSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionPKAPI(APIView):
    def check_submission_is_complete(
        self, report: Report, submission: Submission
    ) -> bool:
        # If it's Form Reponse for the submission instruction, we need to check if the submission has all the required questions
        if report.submission_instruction.type == "RESPONSE_REQUIRED":
            if len(report.submission_instruction.questions) != len(
                submission.get("submission_content")
            ):
                return False

            for question in report.submission_instruction.questions:
                if question.get("type") == "document":
                    if not submission.get("file_urls"):
                        return False

        return True

    def get_submission(self, _, pk):
        return get_object_or_404(Submission, pk=pk)

    def get(self, _, pk):
        submission = self.get_submission(self, pk)
        serializer = SubmissionSerializer(submission, read_only=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _, pk):
        submission = self.get_submission(self, pk)
        submission.delete()
        return Response(
            {"message": MSG_CONST.MSG_SUBMISSION_DELETED},
            status=status.HTTP_204_NO_CONTENT,
        )

    def put(self, req, pk):
        token_data = getattr(req, "token_data", None)
        user = User.objects.get(id=token_data["user_id"], deleted_at=None)

        submission = Submission.objects.get(id=pk)
        report = submission.report_schedule.report
        school = School.objects.get(id=submission.school.id)

        if req.data.get("assigned_member_id"):
            assigned_user = User.objects.get(
                id=req.data["assigned_member_id"], deleted_at=None
            )
            req.data["assigned_member"] = assigned_user
            del req.data["assigned_member_id"]

        else:
            req.data["assigned_member"] = None

            if "assigned_member_id" in req.data:
                del req.data["assigned_member_id"]

        new_submission_status = req.data.get("status", submission.status)
        school_submission_date = req.data.get(
            "school_submission_date", submission.school_submission_date
        )

        if user.role not in [UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value]:
            if not self.check_submission_is_complete(report, req.data):
                return Response(
                    {"message": "Submission is not complete"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_submission_status = SubmissionStatus.PENDING.value
            school_submission_date = req.data.get(
                "school_submission_date", datetime.now()
            )

            # Set up notifications for all agency level admin users
            agency_admin_users = User.objects.filter(
                role__in=[UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value],
                agency=school.agency,
                deleted_at=None,
            )

            notification_service.create_notifications(
                notifications=[
                    Notification(
                        id=generateUniqueID(),
                        description=f"New submission from {school.name} for {report.name}",
                        type=NotificationType.REPORT_SUBMISSION,
                        receiver_id=admin_user.id,
                        report_id=report.id,
                        school_ids=[school.id],
                        created_at=datetime.now(),
                        title=f"New submission from {school.name}",
                    )
                    for admin_user in agency_admin_users
                ],
                create_batch=True,
            )

        return process_serializer(
            SubmissionCreateAndUpdateSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            status=new_submission_status,
            updated_by=user,
            school=school,
            school_submission_date=school_submission_date,
            original_object=submission,
        )


class SubmissionFilterAPI(APIView):

    def get(self, _, type, pk):
        data = filterSchoolReports(type, pk)
        return Response(data, status=status.HTTP_200_OK)


class SubmissionsAdminByReportAPI(APIView):

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        selected_agency = token_data["agency"]
        return Response(
            get_reports_with_multiple_submissions(req, selected_agency),
            status=status.HTTP_200_OK,
        )


class SubmissionsAdminBySchoolAPI(APIView):

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        selected_agency = token_data["agency"]

        return Response(
            get_schools_with_multiple_submissions(req, selected_agency),
            status=status.HTTP_200_OK,
        )


class SubmissionsBySchoolAPI(APIView):

    def get(self, _, school_pk):
        fields = {"school_id": school_pk}
        data = filterObjects(fields, Submission)
        serializer = SubmissionSchoolDetailSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionMessageAPI(APIView):

    def post(self, req, submission_pk):
        data = req.data
        data["submission"] = submission_pk
        token_data = getattr(req, "token_data", None)
        data["sender"] = token_data["user_id"]

        return process_serializer(SubmissionMessageSerializer, data)

    def get(self, _, submission_pk):
        fields = {"submission_id": submission_pk}
        data = filterObjects(fields, SubmissionMessage)
        serializer = SubmissionMessageDetailSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionAssignedUserAPI(APIView):
    def post(self, req):

        token_data = getattr(req, "token_data", None)
        current_user_id = token_data["user_id"]

        current_user = User.objects.get(id=current_user_id, deleted_at=None)

        current_user_role = current_user.role

        if current_user_role not in [
            UserRole.AGENCY_USER.value,
            UserRole.AGENCY_ADMIN.value,
            UserRole.SCHOOL_ADMIN.value,
        ]:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        submission_ids = req.data["submission_ids"]
        assigned_user_id = req.data["assigned_user_id"]

        if not submission_ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not assigned_user_id:
            assigned_user = None
        else:
            assigned_user = User.objects.get(id=assigned_user_id, deleted_at=None)

        submissions = Submission.objects.filter(id__in=submission_ids)

        for submission in submissions:
            submission.assigned_member = assigned_user
            submission.save()

        serializer = SubmissionSerializer(submissions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionAssignEvaluatorAPI(APIView):
    def post(self, req):
        token_data = getattr(req, "token_data", None)
        current_user_id = token_data["user_id"]
        current_user = User.objects.get(id=current_user_id, deleted_at=None)
        current_user_role = current_user.role

        if current_user_role not in [
            UserRole.AGENCY_USER.value,
            UserRole.AGENCY_ADMIN.value,
        ]:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        submission_ids = req.data["submission_ids"]
        evaluator_id = req.data["evaluator_id"]

        if not submission_ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not evaluator_id:
            evaluator = None
        else:
            evaluator = User.objects.get(
                id=evaluator_id,
                deleted_at=None,
                role__in=[
                    UserRole.AGENCY_ADMIN.value,
                    UserRole.AGENCY_USER.value,
                ],
            )

        submissions = Submission.objects.filter(id__in=submission_ids)
        for submission in submissions:
            submission.evaluator = evaluator
            submission.save()

        serializer = SubmissionSerializer(submissions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionDownloadAPI(APIView):
    def get(self, req, pk):
        submission = get_object_or_404(Submission, pk=pk)

        # Use mock AWS service instead of direct boto3 calls
        s3_client = mock_aws_service.get_s3_client()

        for file_url in submission.file_urls:
            file_url["file_url"] = generate_get_presigned_url(
                urlparse(file_url.get("file_url")).path[1:], s3_client
            )

        serializer = SubmissionSerializer(submission, read_only=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SchoolSubmissionDownloadAPI(APIView):
    def get(self, req, pk):
        school = get_object_or_404(School, pk=pk)

        # Gather all submissions for this school
        submissions = Submission.objects.filter(
            school=school,
        ).exclude(status=SubmissionStatus.INCOMPLETED.value)

        for submission in submissions:
            for file_url in submission.file_urls:
                file_url["file_url"] = generate_get_presigned_url(
                    urlparse(file_url.get("file_url")).path[1:]
                )

        serializer = SubmissionSerializer(submissions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportSubmissionDownloadAPI(APIView):
    def get(self, req, pk):
        report = get_object_or_404(Report, schedules__id=pk)

        # Gather all submissions for this report
        submissions = Submission.objects.filter(report_schedule__report=report).exclude(
            status=SubmissionStatus.INCOMPLETED.value
        )

        for submission in submissions:
            for file_url in submission.file_urls:
                file_url["file_url"] = generate_get_presigned_url(
                    urlparse(file_url.get("file_url")).path[1:]
                )

        serializer = SubmissionSerializer(submissions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
