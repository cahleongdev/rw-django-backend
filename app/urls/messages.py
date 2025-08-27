from django.urls import path

from app.views.messages import MessageAPI, MessagePKAPI

urlpatterns = [
    path("", MessageAPI.as_view(), name="message-list-create"),
    path("<str:pk>/", MessagePKAPI.as_view(), name="message-detail"),
]
