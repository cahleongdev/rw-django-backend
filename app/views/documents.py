from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.documents import Document
from app.serializers.documents import DocumentSerializer, DocumentWithRelatedSerializer
from app.utils.pagination import CustomPagination


class DocumentAPI(APIView):
    def post(self, req):
        token_data = getattr(req, "token_data", None)
        data = req.data.copy()
        data["created_by"] = token_data["email"]

        serializer = DocumentSerializer(data=data, context={"request": req})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, req):
        # How is this seperate from the files API?????
        parent_type = req.query_params.get("parent_type")
        parent_id = req.query_params.get("parent_id")

        queryset = Document.objects.all()

        if parent_type:
            if parent_type == "board":
                queryset = queryset.filter(
                    parent_type__model="school", year="Board Documents"
                )
            elif parent_type == "school":
                queryset = queryset.filter(parent_type__model="school").exclude(
                    year="Board Documents"
                )
            else:
                queryset = queryset.filter(parent_type__model=parent_type)

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        serializer = DocumentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocumentDetailAPI(APIView):
    def get_document(self, pk):
        return get_object_or_404(Document, pk=pk)

    def get(self, req, pk):
        document = self.get_document(pk)
        serializer = DocumentWithRelatedSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        document = self.get_document(pk)
        serializer = DocumentSerializer(document, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, req, pk):
        document = self.get_document(pk)
        document.delete()
        return Response(
            {"message": "Document deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
