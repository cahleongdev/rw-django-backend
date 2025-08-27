from django.urls import path

from app.views.files import (
    GenerateDownloadPresignedUrl,
    GenerateGetPresignedURLAPI,
    GeneratePresignedURLAPI,
    RemoveFileAPI,
)

urlpatterns = [
    path(
        "generate_presigned_url/",
        GeneratePresignedURLAPI.as_view(),
        name="generate_presigned_url",
    ),
    path(
        "generate_get_presigned_url/",
        GenerateGetPresignedURLAPI.as_view(),
        name="generate_get_presigned_url",
    ),
    path("remove_file/", RemoveFileAPI.as_view(), name="remove_file"),
    path(
        "generate_download_url/",
        GenerateDownloadPresignedUrl.as_view(),
        name="generate_download_url",
    ),
]
