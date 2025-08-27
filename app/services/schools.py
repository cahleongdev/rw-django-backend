from django.db.models import Count

from app.models.schools import School
from app.serializers.reports import ReportCategorySerializer, ReportSerializer
from app.serializers.submission_instructions import SubmissionInstructionSerializer


def get_schools_with_multiple_submissions(req, selected_agency):

    schools = (
        School.objects.filter(agency=selected_agency)
        .annotate(submission_count=Count("submission"))
        .prefetch_related(
            "submission_set__report_schedule",
            "submission_set__report_schedule__report",
            "submission_set__report_schedule__report__categories",
            "submission_set__assigned_member",
        )
        .order_by("id")
    )

    # Denest this so that we can pull based on the school.submission_set.report_schedule
    response = []
    for school in schools:
        school_data = {
            "id": school.id,
            "name": school.name,
            "gradeserved": school.gradeserved,
            "submissions": [],
        }

        submissions = list(school.submission_set.all())
        for submission in submissions:
            print(submission.report_schedule.report.id)
            submission_data = {
                "id": submission.id,
                "report_id": submission.report_schedule.report_id,
                "report_name": submission.report_schedule.report_name,
                "report_categories": ReportCategorySerializer(
                    submission.report_schedule.report.categories.all(), many=True
                ).data,
                "due_date": submission.report_schedule.schedule_time,
                "submission_date": submission.created_at,
                "status": submission.status,
                "assigned_member_id": (
                    submission.assigned_member.id
                    if submission.assigned_member
                    else None
                ),
                "assigned_member_name": (
                    submission.assigned_member.get_full_name()
                    if submission.assigned_member
                    else None
                ),
                "submission_instruction": SubmissionInstructionSerializer(
                    submission.report_schedule.report.submission_instruction
                ).data,
            }

            school_data["submissions"].append(submission_data)

        school_data["report"] = (
            ReportSerializer(
                school.submission_set.first().report_schedule.report,
                read_only=True,
            ).data
            if school.submission_set.first()
            else None
        )

        response.append(school_data)

    return response
