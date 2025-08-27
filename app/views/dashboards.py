from django.db.models import Count, F, Max
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import School, User
from app.models.reports import Report
from app.models.submissions import Submission
from app.services.agencies import get_schools_by_agency
from app.services.base import filterObjects


class DashboardsGlanceAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            agency_id = token_data["agency"]

            # Get values from query parameters instead of request body
            school_id = req.query_params.get("school_id")
            report_id = req.query_params.get("report_id")
            domain = req.query_params.get("domain")
            year = req.query_params.get("year")
            month = req.query_params.get("month")
            team_id = req.query_params.get("team_id")

            # Base filter with common fields
            base_filters = {"agency_id": agency_id}
            if school_id:
                base_filters["school_id"] = school_id
            if report_id:
                base_filters["report_schedule__report_id"] = report_id
            if team_id:
                base_filters["assigned_member_id"] = team_id
            if domain:
                # Filter submissions whose reports have the specified domain
                base_filters["report_schedule__report__domain"] = domain
            # Add year and month filters if provided
            if year:
                base_filters["report_schedule__schedule_time__year"] = year
            if month:
                base_filters["report_schedule__schedule_time__month"] = month

            # Get base queryset with common filters
            base_submissions = filterObjects(base_filters, Submission)

            # Get submitted submissions from base queryset
            submitted_submissions = base_submissions.filter(
                school_submission_date__isnull=False
            )

            # Timeliness calculations from submitted submissions
            on_time_count = submitted_submissions.filter(
                school_submission_date__lte=F("report_schedule__schedule_time")
            ).count()

            late_count = submitted_submissions.filter(
                school_submission_date__gt=F("report_schedule__schedule_time")
            ).count()

            # Status counts from base queryset
            completed_submissions = base_submissions.filter(status="completed")
            pending_submissions = base_submissions.filter(status="pending")
            returned_submissions = base_submissions.filter(status="returned")
            incomplete_submissions = base_submissions.filter(status="incompleted")

            # Calculate counts
            total_submissions = base_submissions.count()
            submitted_count = submitted_submissions.count()
            not_submitted_count = total_submissions - submitted_count
            past_due_count = not_submitted_count

            response_data = {
                "submitted": {
                    "submitted": submitted_count,
                    "not_submitted": not_submitted_count,
                },
                "timeliness": {
                    "on_time": on_time_count,
                    "late": late_count,
                    "past_due": past_due_count,
                },
                "status": {
                    "completed": completed_submissions.count(),
                    "pending": pending_submissions.count(),
                    "returned": returned_submissions.count(),
                    "incomplete": incomplete_submissions.count(),
                },
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while processing request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DashboardsOverdueReportsAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            agency_id = token_data["agency"]

            school_ids = get_schools_by_agency(agency_id)

            schools_with_counts = (
                School.objects.filter(id__in=school_ids)
                .values("id", "name")
                .annotate(submission_count=Count("submission"))
                .order_by("name")
            )

            response_data = [
                {
                    "school_name": school["name"],
                    "submission_count": school["submission_count"],
                }
                for school in schools_with_counts
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching overdue reports"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardsOutstandingReportsAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            agency_id = token_data["agency"]

            # Get all submissions for this agency
            submissions = Submission.objects.filter(agency_id=agency_id)

            # Define the statuses we want to track
            status_categories = ["incompleted", "returned", "pending"]

            response_data = {}

            # Process each status category
            for r_status in status_categories:
                # Get submissions for this status
                status_submissions = submissions.filter(status=r_status)

                # Get report counts and latest due date by report_id
                report_counts = status_submissions.values(
                    "report_schedule__report_id"
                ).annotate(
                    count=Count("school_id", distinct=True),
                    last_date=Max(
                        "report_schedule__schedule_time"
                    ),  # Get the latest due date from schedule_time
                )

                # Create the status category data
                status_key = {
                    "incompleted": "Incomplete",
                    "returned": "Returned",
                    "pending": "Pending",
                }[r_status]

                response_data[status_key] = {
                    "count": status_submissions.count(),
                    "reports": {},  # Initialize reports dictionary
                }

                # Add report-specific counts with report names and last due date
                for report_data in report_counts:
                    report_id = report_data["report_schedule__report_id"]
                    try:
                        report = Report.objects.get(id=report_id)
                        report_name = report.name
                        response_data[status_key]["reports"][report_name] = {
                            "count": report_data["count"],
                            "last_date": report_data["last_date"],
                        }
                    except Report.DoesNotExist:
                        continue

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching outstanding reports"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardsFilterValuesAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            agency_id = token_data["agency"]

            # Get only id and name fields
            reports = Report.objects.filter(agency_id=agency_id).values("id", "name")
            schools = School.objects.filter(agency_id=agency_id).values("id", "name")
            domains = (
                Report.objects.filter(agency_id=agency_id)
                .values_list("domain", flat=True)
                .distinct()
            )
            teams = User.objects.filter(agency_id=agency_id, deleted_at=None).values(
                "id", "first_name", "last_name"
            )

            return Response(
                {
                    "reports": list(reports),  # Convert QuerySet to list
                    "schools": list(schools),  # Convert QuerySet to list
                    "domains": list(domains),
                    "teams": list(teams),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching filter values"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
