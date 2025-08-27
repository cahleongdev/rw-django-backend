from collections import defaultdict
from datetime import datetime

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.enumeration import NotificationType, SubmissionStatus
from app.models.notifications import Notification
from app.models.reports import Report, ReportCategory
from app.models.submissions import Submission
from app.models.users import User
from app.serializers.reports import (
    ReportCategorySerializer,
    ReportDetailSerializer,
    ReportSerializer,
)
from app.utils.helper import generateUniqueID
from app.utils.pagination import CustomPagination
from app.views.notifications import notification_service
from app.services.base import process_serializer


class ReportAPI(APIView):
    def get(self, _):
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        serializer = ReportSerializer(data=req.data)
        if serializer.is_valid():
            # Get the user from token data
            token_data = getattr(req, "token_data", None)
            user_id = token_data.get("user_id")
            # Save with the user
            serializer.save(edited_by_id=user_id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportCategoryAPI(APIView):
    def get(self, req):
        token_data = getattr(req, "token_data", None)
        agency_id = None
        if token_data and "agency" in token_data:
            agency_id = token_data["agency"]
        elif hasattr(req.user, "agency") and req.user.agency:
            agency_id = req.user.agency.pk
        categories = ReportCategory.objects.filter(agency_id=agency_id)
        serializer = ReportCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        token_data = getattr(req, "token_data", None)
        agency_id = None
        if token_data and "agency" in token_data:
            agency_id = token_data["agency"]
        elif hasattr(req.user, "agency") and req.user.agency:
            agency_id = req.user.agency.pk
        data = req.data.copy()
        data["agency_id"] = agency_id
        serializer = ReportCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, req):
        token_data = getattr(req, "token_data", None)
        agency_id = None
        if token_data and "agency" in token_data:
            agency_id = token_data["agency"]
        elif hasattr(req.user, "agency") and req.user.agency:
            agency_id = req.user.agency.pk
        updates = req.data.get("updates", [])
        deletes = req.data.get("deletes", [])
        adds = req.data.get("adds", [])
        new_categories = []
        # Update colors
        for update in updates:
            cat_id = update.get("id")
            color = update.get("color")
            if cat_id and color:
                ReportCategory.objects.filter(id=cat_id, agency_id=agency_id).update(
                    color=color
                )
        # Delete categories
        if deletes:
            ReportCategory.objects.filter(id__in=deletes, agency_id=agency_id).delete()
        # Add new categories
        for add in adds:
            name = add.get("name")
            color = add.get("color")
            if name and color:
                category = ReportCategory.objects.create(
                    name=name, color=color, agency_id=agency_id
                )
                new_categories.append(category)
        # Return updated list
        categories = ReportCategory.objects.filter(agency_id=agency_id)
        serializer = ReportCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgencyAdminReportAPI(APIView):
    pagination_class = CustomPagination

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]
        queryset = Report.objects.filter(agency_id=agency)
        serializer = ReportDetailSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportPKAPI(APIView):
    def get_report(self, _, pk):
        return get_object_or_404(Report, pk=pk)

    def get(self, _, pk):
        report = self.get_report(self, pk)
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _, pk):
        report = self.get_report(self, pk)
        report.delete()
        return Response(
            {"message": MSG_CONST.MSG_REPORT_DELETED}, status=status.HTTP_204_NO_CONTENT
        )

    def put(self, req, pk):
        report = self.get_report(self, pk)

        if req.data.get("schedule_type") == "RECURRING_DATES":
            req.data["recurring_period"] = req.data["recurring_period"].upper()

        token_data = getattr(req, "token_data", None)
        user_id = token_data.get("user_id")

        return process_serializer(
            ReportSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=report,
            edited_by_id=user_id,
        )


class ReportDuplicateAPI(APIView):
    def post(self, req, pk):
        original_report = get_object_or_404(Report, id=pk)

        # Get token data for the user
        token_data = getattr(req, "token_data", None)
        user_id = token_data.get("user_id") if token_data else None

        # Serialize the original report (this includes all related objects)
        serializer = ReportSerializer(original_report)
        report_data = serializer.data

        # Modify the data for duplication
        report_data["name"] = f"{original_report.name} (Copy)"
        report_data["approved"] = False

        # Remove ID fields to create new objects
        report_data.pop("id", None)
        if "scoring" in report_data and report_data["scoring"]:
            report_data["scoring"].pop("id", None)

        if (
            "submission_instruction" in report_data
            and report_data["submission_instruction"]
        ):
            report_data["submission_instruction"].pop("id", None)

        if "schedules" in report_data:
            for schedule in report_data["schedules"]:
                schedule.pop("id", None)

        # Create the new report using the serializer
        new_serializer = ReportSerializer(data=report_data)
        if new_serializer.is_valid():
            new_serializer.save(edited_by_id=user_id)
            return Response(
                {
                    "message": "Report duplicated successfully",
                    "new_report_id": new_serializer.instance.id,
                    "new_report_name": new_serializer.instance.name,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(new_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportBulkDeleteAPI(APIView):
    def delete(self, req):
        try:
            report_ids = req.data.get("report_ids", [])

            if not report_ids:
                return Response(
                    {"error": "No report IDs provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get all reports that exist from the provided IDs
            reports_to_delete = Report.objects.filter(id__in=report_ids)
            deleted_ids = list(reports_to_delete.values_list("id", flat=True))

            # Delete the reports
            reports_to_delete.delete()

            return Response(
                {
                    "message": "Reports deleted successfully",
                    "deleted_reports": deleted_ids,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting reports"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReportSchoolAssignAPI(APIView):
    def post(self, req):
        try:
            report_id = req.data.get("report_id")
            school_ids = req.data.get("school_ids", [])

            if not report_id:
                return Response(
                    {"error": "Report ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate the report has all needed objects before allowing assignment
            report = get_object_or_404(Report, id=report_id)

            # Check if report is complete - validate required fields
            if not all(
                [
                    report.name,
                    report.agency_id,
                    report.schedules.exists(),
                    report.submission_instruction,
                ]
            ):
                return Response(
                    {"error": "Report is not complete - missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the report
            with transaction.atomic():
                # Get existing school reports for this report
                existing_schools = Submission.objects.filter(
                    report_schedule__report=report
                ).values_list("school_id", flat=True)

                # Find schools to remove (schools that exist but are not in the new list)
                schools_to_remove = set(existing_schools) - set(school_ids)

                notifications = []
                # Delete SchoolReport entries for removed schools
                if schools_to_remove:
                    # This is obsolete
                    Submission.objects.filter(
                        report_schedule__report=report, school_id__in=schools_to_remove
                    ).delete()

                    user_school_mapping = defaultdict(set)
                    for user in User.objects.filter(
                        schools__id__in=schools_to_remove, deleted_at=None
                    ):
                        for school in user.schools.filter(id__in=schools_to_remove):
                            user_school_mapping[user.id].add(school.id)

                    for user_id, school_ids in user_school_mapping.items():
                        if len(school_ids) > 1:
                            notifications.append(
                                Notification(
                                    id=generateUniqueID(),
                                    description=f"Report {report.name} removed from multiple schools",
                                    type=NotificationType.MULTIPLE_REPORT_UNASSIGNMENT,
                                    receiver_id=user_id,
                                    report_id=report_id,
                                    school_ids=school_ids,
                                    created_at=datetime.now(),
                                )
                            )

                        else:
                            notifications.append(
                                Notification(
                                    id=generateUniqueID(),
                                    description=f"Report {report.name} removed from school {list(school_ids)[0]}",
                                    type=NotificationType.REPORT_UNASSIGNMENT,
                                    receiver_id=user_id,
                                    report_id=report_id,
                                    school_ids=school_ids,
                                    created_at=datetime.now(),
                                )
                            )

                # Find new schools to add
                new_school_ids = set(school_ids) - set(existing_schools)
                # Create new SchoolReport entries
                school_reports = []

                for school_id in new_school_ids:
                    for report_schedule in report.schedules.all():
                        school_reports.append(
                            Submission(
                                id=generateUniqueID(),
                                school_id=school_id,
                                report_schedule=report_schedule,
                                agency_id=report.agency_id,
                                status=SubmissionStatus.INCOMPLETED.value,
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                created_by_id=report.edited_by_id,
                            )
                        )

                # Bulk create the new assignments
                if school_reports:
                    Submission.objects.bulk_create(school_reports)

                    user_school_mapping = defaultdict(set)
                    for user in User.objects.filter(
                        schools__id__in=new_school_ids, deleted_at=None
                    ):
                        for school in user.schools.filter(id__in=new_school_ids):
                            user_school_mapping[user.id].add(school.id)

                    for user_id, school_ids in user_school_mapping.items():
                        if len(school_ids) > 1:
                            notifications.append(
                                Notification(
                                    id=generateUniqueID(),
                                    description=f"Report {report.name} assigned to multiple schools",
                                    type=NotificationType.MULTIPLE_REPORT_ASSIGNMENT,
                                    receiver_id=user_id,
                                    report_id=report_id,
                                    school_ids=school_ids,
                                    created_at=datetime.now(),
                                )
                            )

                        else:
                            notifications.append(
                                Notification(
                                    id=generateUniqueID(),
                                    description=f"Report {report.name} assigned to school {list(school_ids)[0]}",
                                    type=NotificationType.REPORT_ASSIGNMENT,
                                    receiver_id=user_id,
                                    report_id=report_id,
                                    school_ids=school_ids,
                                    created_at=datetime.now(),
                                )
                            )

                if notifications:
                    notification_service.create_notifications(
                        notifications, create_batch=True
                    )

            # Get all assigned schools for response
            all_school_reports = Submission.objects.filter(
                report_schedule__report=report
            ).select_related("school")

            assigned_schools = [
                {
                    "id": sr.school.id,
                    "name": sr.school.name,
                    "assigned_at": sr.created_at,
                }
                for sr in all_school_reports
            ]

            return Response(
                {
                    "message": "Schools assigned successfully",
                    "report_id": report_id,
                    "assigned_schools": assigned_schools,
                },
                status=status.HTTP_200_OK,
            )

        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": "An error occurred while assigning schools"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, req):
        try:
            report_id = req.query_params.get("report_id")

            if not report_id:
                return Response(
                    {"error": "Report ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get all assigned schools for this report
            school_reports = Submission.objects.filter(
                report_schedule__report_id=report_id
            ).select_related("school")

            assigned_schools = [
                {
                    "id": sr.school.id,
                    "name": sr.school.name,
                    "assigned_at": sr.created_at,
                }
                for sr in school_reports
            ]

            return Response(
                {"report_id": report_id, "assigned_schools": assigned_schools},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching assigned schools"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, req):
        try:
            report_id = req.data.get("report_id")
            school_ids = req.data.get("school_ids", [])

            if not report_id:
                return Response(
                    {"error": "Report ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not school_ids:
                return Response(
                    {"error": "No schools provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            report = Report.objects.get(id=report_id)

            # Delete the specified assignments
            deleted_count = Submission.objects.filter(
                report_schedule__report_id=report_id, school_id__in=school_ids
            ).delete()[0]

            # Get remaining assigned schools
            remaining_school_reports = Submission.objects.filter(
                report_schedule__report_id=report_id
            ).select_related("school")

            notifications = []

            user_school_mapping = defaultdict(list)
            for user in User.objects.filter(school_id__in=school_ids, deleted_at=None):
                user_school_mapping[user.id].append(user.school_id)

            for user_id, school_ids in user_school_mapping.items():
                if len(school_ids) > 1:
                    notifications.append(
                        Notification(
                            id=generateUniqueID(),
                            description=f"Report {report.name} removed from multiple schools",
                            type=NotificationType.MULTIPLE_REPORT_UNASSIGNMENT,
                            receiver_id=user_id,
                            report_id=report_id,
                            school_ids=school_ids,
                            created_at=datetime.now(),
                        )
                    )

                else:
                    notifications.append(
                        Notification(
                            id=generateUniqueID(),
                            description=f"Report {report.name} removed from school {school_ids[0]}",
                            type=NotificationType.REPORT_UNASSIGNMENT,
                            receiver_id=user_id,
                            report_id=report_id,
                            school_ids=school_ids,
                            created_at=datetime.now(),
                        )
                    )

            notification_service.create_notifications(notifications, create_batch=True)

            remaining_schools = [
                {
                    "id": sr.school.id,
                    "name": sr.school.name,
                    "assigned_at": sr.created_at,
                }
                for sr in remaining_school_reports
            ]

            return Response(
                {
                    "message": f"{deleted_count} school assignments removed",
                    "report_id": report_id,
                    "remaining_schools": remaining_schools,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An error occurred while removing school assignments"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
