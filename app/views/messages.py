from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import app.constants.msg as MSG_CONST
from app.models.messages import Message
from app.serializers.messages import MessageSerializer
from app.services.base import filterObjects, process_serializer


class MessageAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            send_fields = {
                "sender": token_data["user_id"],
                "receiver": req.GET.get("receiver"),
            }
            send_messages = filterObjects(send_fields, Message)

            receive_fields = {
                "sender": req.GET.get("receiver"),
                "receiver": token_data["user_id"],
            }
            receive_messages = filterObjects(receive_fields, Message)

            # Serialize both sets of messages
            sent_serializer = MessageSerializer(send_messages, many=True)
            received_serializer = MessageSerializer(receive_messages, many=True)

            # Combine them in a structured response
            response_data = {
                "sent_messages": sent_serializer.data,
                "received_messages": received_serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred while fetching messages"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, req):
        token_data = getattr(req, "token_data", None)
        data = {
            "sender": token_data["user_id"],
            "receiver": req.data["receiver"],
            "title": req.data["title"],
            "content": req.data["content"],
            "type": req.data["type"],
            "file_urls": req.data.get("file_urls", []),
        }
        return process_serializer(MessageSerializer, data)


class MessagePKAPI(APIView):
    def get(self, _, pk):
        message = get_object_or_404(Message, pk=pk)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        message = get_object_or_404(Message, pk=pk)
        return process_serializer(
            MessageSerializer,
            req.data,
            success_status=status.HTTP_200_OK,
            original_object=message,
        )

    def delete(self, _, pk):
        message = get_object_or_404(Message, pk=pk)
        message.delete()
        return Response(
            {"message": MSG_CONST.MSG_NORMAL_DELETE}, status=status.HTTP_204_NO_CONTENT
        )
