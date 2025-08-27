from django.urls import path

from app.views.documents import DocumentAPI, DocumentDetailAPI

urlpatterns = [
    path("", DocumentAPI.as_view(), name="documents"),
    path("<str:pk>/", DocumentDetailAPI.as_view(), name="document-detail"),
]
