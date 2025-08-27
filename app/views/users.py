from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.models.schools import School
from app.models.users import User
from app.serializers.users import (
    MessageUserSerializer,
    SchoolAssignedUserSerializer,
    UserSerializer,
)

from app.services.users import user_invitation, send_user_notifications
from app.services.base import filterObjects

from app.utils.pagination import CustomPagination
from app.utils.helper import mask_email, mask_phone
from app.enumeration.mfa import MFAMethod
from app.enumeration.user_role import UserRole
import app.constants.msg as MSG_CONST

User = get_user_model()


class UserPKAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, req, pk):
        user = get_object_or_404(User, pk=pk)

        serializer = UserSerializer(user, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, req, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(
            {"message": MSG_CONST.MSG_USER_DELETED}, status=status.HTTP_200_OK
        )

    def get(self, req, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, read_only=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SchoolUserAPI(APIView):
    def get(self, req, role, school):
        paginator = CustomPagination()

        if role == "School_User":
            queryset = User.objects.filter(
                Q(role="School_User") | Q(role="School_Admin"),
                schools__id=school,
                deleted_at=None,
            )
        else:
            queryset = User.objects.filter(
                role=role,
                schools__id=school,
                deleted_at=None,
            )

        paginated_queryset = paginator.paginate_queryset(queryset, req)
        serializer = SchoolAssignedUserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class AgencyAdminUserAPI(APIView):

    def get(self, req):
        token_data = getattr(req, "token_data", None)
        agency = token_data["agency"]
        fields = {"agency": agency}
        data = filterObjects(fields, User)
        serializer = UserSerializer(data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SchoolAdminUserAPI(APIView):
    def get(self, _, school):
        # Get all users in the schools this this user is associated with

        data = User.objects.filter(schools__id=school).distinct()

        serializer = UserSerializer(data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateAPI(APIView):
    @transaction.atomic
    def post(self, req):
        token_data = getattr(req, "token_data", None)
        agency_id = token_data.get("agency", req.user.agency.pk)
        send_invite = req.data.pop("send_invite", False)
        
        req.data["agency"] = agency_id
        
        # Set user is_active based on whether invitation will be sent
        if send_invite:
            req.data["is_active"] = False
        else:
            req.data["is_active"] = None

        serializer = UserSerializer(data=req.data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_user = serializer.save()
        
        # Send notifications to relevant users about the new user
        send_user_notifications(new_user)
        
        if send_invite:
            inviting_user = req.user
            user_invitation(req, new_user, inviting_user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SuperAdminUsersAPI(APIView):
    def get(self, req):
        token_data = getattr(req, "token_data", None)
        if token_data["role"] != "Super_Admin":
            return Response(
                {"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        users = User.objects.filter(deleted_at=None)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageUsersAPI(APIView):
    def get(self, req):
        try:
            token_data = getattr(req, "token_data", None)
            current_user_id = token_data["user_id"]
            current_user = User.objects.get(id=current_user_id)

            current_user_role = UserRole(current_user.role)

            if current_user_role in [UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN]:
                users = (
                    User.objects.filter(agency=current_user.agency, deleted_at=None)
                    .exclude(id=current_user.id)
                    .prefetch_related(
                        Prefetch("schools", queryset=School.objects.only("id", "name"))
                    )
                )
            else:
                users = (
                    User.objects.filter(
                        schools__in=current_user.schools.all(),
                        deleted_at=None,
                    )
                    .exclude(id=current_user.id)
                    .prefetch_related(
                        Prefetch("schools", queryset=School.objects.only("id", "name"))
                    )
                )

            serializer = MessageUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Error fetching users"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserMeAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        print(serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMFAContactAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        mfa_methods = user.mfa_method or []
        result = {}
        if MFAMethod.SMS in mfa_methods or MFAMethod.VOICE in mfa_methods:
            result["phone"] = mask_phone(user.mfa_phone) if user.mfa_phone else None
        if MFAMethod.EMAIL in mfa_methods:
            result["email"] = mask_email(user.mfa_email) if user.mfa_email else None
        return Response(result)
