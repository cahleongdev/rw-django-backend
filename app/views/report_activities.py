from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models.report_activities import ReportActivity
from app.serializers.report_activities import ReportActivitySerializer


class ReportActivityAPI(APIView):
    def get(self, req):
        try:
            report_id = req.query_params.get("report_id")
            if not report_id:
                return Response(
                    {"error": "Report ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            activities = ReportActivity.objects.filter(
                report_id=report_id
            ).select_related("user")

            serializer = ReportActivitySerializer(activities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching activities"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]
            serializer = ReportActivitySerializer(data=req.data)
            if serializer.is_valid():
                serializer.save(user_id=user_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "An error occurred while creating the activity"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReportActivityDetailAPI(APIView):
    def get(self, req, activity_id):
        try:
            activity = get_object_or_404(ReportActivity, id=activity_id)
            serializer = ReportActivitySerializer(activity)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ReportActivity.DoesNotExist:
            return Response(
                {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching the activity"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, req, activity_id):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]

            activity = get_object_or_404(ReportActivity, id=activity_id)

            # Only allow the creator to update
            if activity.user_id != user_id:
                return Response(
                    {"error": "Not authorized to update this activity"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ReportActivitySerializer(activity, data=req.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "An error occurred while updating the activity"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, req, activity_id):
        try:
            token_data = getattr(req, "token_data", None)
            user_id = token_data["user_id"]

            activity = get_object_or_404(ReportActivity, id=activity_id)

            # Only allow the creator to delete
            if activity.user_id != user_id:
                return Response(
                    {"error": "Not authorized to delete this activity"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            activity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting the activity"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
