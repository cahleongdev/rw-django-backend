import uuid

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.services.files import (
    generate_download_url,
    generate_get_presigned_url,
    generate_presigned_url,
    remove_file,
)


class GeneratePresignedURLAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, req):
        file_type = req.GET.get("file_type")
        file_name = req.GET.get("file_name")
        type = req.GET.get("type") or "default"

        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]

        unique_id = str(uuid.uuid4())

        if type == "avatar":
            # Publically accessible bucket
            upload_path = f"avatar/{unique_id}"

        else:
            upload_path = f"{agency}/{unique_id}"

        generated_url = generate_presigned_url(upload_path, file_name, file_type)

        return Response(
            {"url": generated_url, "file_name": upload_path}, status=status.HTTP_200_OK
        )


class GenerateGetPresignedURLAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, req):
        incoming_file_name = req.GET.get("file_name")
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]

        file_name = f"{agency}/{incoming_file_name}"

        generated_url = generate_get_presigned_url(file_name)
        return Response(generated_url, status=status.HTTP_200_OK)


class GenerateDownloadPresignedUrl(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, req):
        incoming_file_name = req.GET.get("file_name")
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]

        file_name = f"{agency}/{incoming_file_name}"

        generated_url = generate_download_url(file_name)
        return Response(generated_url, status=status.HTTP_200_OK)


class RemoveFileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, req):
        incoming_file_name = req.GET.get("file_name")
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]

        file_name = f"{agency}/{incoming_file_name}"

        result = remove_file(file_name)

        return Response(result, status=status.HTTP_200_OK)
