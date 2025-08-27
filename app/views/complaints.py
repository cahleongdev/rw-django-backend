from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.complaints import Complaint
from app.serializers.complaints import ComplaintListSerializer, ComplaintSerializer
from app.services.base import (
    filterObjects,
    get_paginated_filtered_data,
    process_serializer,
)
from app.utils.pagination import CustomPagination


class ComplaintAPI(APIView):
    def get(self, req):
        fields = {
            "assigned_member_id": req.GET.get("assigned_member"),
            "status": req.GET.get("status"),
            "school_id": req.GET.get("school"),
        }
        print(req.GET.get("school"), req.GET.get("assigned_member"))
        data = filterObjects(fields, Complaint)
        serializer = ComplaintListSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        return process_serializer(ComplaintSerializer, req.data)


class AgencyAdminComplaintAPI(APIView):
    pagination_class = CustomPagination

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]
        filter_kwargs = {"agency_id": agency}
        return get_paginated_filtered_data(
            req=req,
            model=Complaint,
            serializer_class=ComplaintListSerializer,
            filter_kwargs=filter_kwargs,
            page_size=10,
        )


class ComplaintPKAPI(APIView):
    def get_complaint(self, _, pk):
        return get_object_or_404(Complaint, pk=pk)

    def get(self, _, pk):
        complaint = self.get_complaint(self, pk)
        serializer = Complaint(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _, pk):
        complaint = self.get_complaint(self, pk)
        complaint.delete()
        return Response(
            {"message": MSG_CONST.MSG_COMPLAINT_DELETED},
            status=status.HTTP_204_NO_CONTENT,
        )

    def put(self, req, pk):
        complaint = self.get_complaint(self, pk)
        return process_serializer(
            ComplaintSerializer,
            data=req.data,
            success_status=status.HTTP_200_OK,
            original_object=complaint,
        )
