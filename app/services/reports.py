from django.db.models import Count

from app.models.reports import Report
from app.serializers.reports import ReportCategorySerializer


def get_reports_with_multiple_submissions(req, selected_agency):
    reports = (
        Report.objects.filter(agency=selected_agency)
        .annotate(submission_count=Count("schedules"))
        .filter(submission_count__gt=0)
        .prefetch_related(
            "categories",
            "schedules__submission_set__school",
            "schedules__submission_set__assigned_member",
        )
        .order_by("id")
    )

    return [
        {
            "id": report.id,
            "name": report.name,
            "categories": ReportCategorySerializer(
                report.categories.all(), many=True
            ).data,
            "due_date": report.due_date,
            "submissions": [
                {
                    "id": submission.id,
                    "school_id": submission.school_id,
                    "school_name": submission.school.name,
                    "due_date": submission.report_schedule.schedule_time,
                    "submission_date": submission.school_submission_date,
                    "status": submission.status,
                    "assigned_member_id": submission.assigned_member_id,
                    "assigned_member_name": (
                        submission.assigned_member.get_full_name()
                        if submission.assigned_member
                        else None
                    ),
                    "report_id": submission.report_schedule.report_id,
                }
                for schedule in report.schedules.all()
                for submission in schedule.submission_set.all()
            ],
        }
        for report in reports
    ]
