from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from app.models.agencies import Agency
from app.models.users import User
from app.models.reports import Report
from app.serializers.agencies import AgencySerializer   
from app.serializers.users import UserSerializer
from app.serializers.reports import ReportSerializer

from app.services.base import get_filtered_data, process_serializer
from app.services.users import user_invitation, send_user_notifications

from app.utils.pagination import CustomPagination

import app.constants.msg as MSG_CONST
from app.enumeration.user_role import UserRole

class AgencyAPI(APIView):
    paginationClass = CustomPagination

    def get(self, req):
        filter_fields = {}
        title = req.GET.get("title")
        if title:
            filter_fields["title"] = title
        return Response(get_filtered_data(
            model=Agency,
            serializer_class=AgencySerializer,
            filter_kwargs=filter_fields,
        ), status=status.HTTP_200_OK)

    def post(self, req):
        return process_serializer(AgencySerializer, req.data)


class AgencyPKAPI(APIView):
    def get_agency(self, _, pk):
        return get_object_or_404(Agency, pk=pk)

    def get(self, _, pk):
        agency = self.get_agency(self, pk)
        serializer = AgencySerializer(agency)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _, pk):
        agency = self.get_agency(self, pk)
        agency.delete()
        return Response(
            {"message": MSG_CONST.MSG_AGENCY_DELETED}, status=status.HTTP_204_NO_CONTENT
        )

    def put(self, req, pk):
        agency = self.get_agency(self, pk)
        return process_serializer(
            AgencySerializer,
            data=req.data,
            success_status=status.HTTP_200_OK,
            original_object=agency,
        )

class AgencyUsersAPI(APIView):
    def get(self, req, pk):
        filter_kwargs = {
            "agency": pk, 
            "role__in": [UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value],
            "deleted_at": None  # Only show non-deleted users
        }
        users = User.objects.filter(**filter_kwargs)
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def post(self, req, pk):
        req.data["agency"] = pk
        req.data["is_active"] = None  # Set as Pending status by default
        serializer = UserSerializer(data=req.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()

        send_user_notifications(new_user)

        # Check if should send invitation immediately
        send_invitation = req.data.get('send_invitation', False)
        if send_invitation:
            new_user.is_active = False  # Set to Inactive when invitation is sent
            new_user.save()
            inviting_user = req.user
            user_invitation(req, new_user, inviting_user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def delete(self, req, pk):
        """Bulk soft delete agency users"""
        user_ids = req.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {"error": "user_ids is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(
            id__in=user_ids, 
            agency=pk,
            role__in=[UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value]
        )
        
        if users.count() != len(user_ids):
            return Response(
                {"error": "Some users not found or already deleted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Soft delete all users
        for user in users:
            user.soft_delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AgencyUserAPI(APIView):
    def get(self, req, pk, user_id):
        user = User.objects.get(id=user_id, agency=pk, deleted_at=None)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, req, pk, user_id):
        """Soft delete individual agency user"""
        try:
            user = User.objects.get(
                id=user_id, 
                agency=pk,
                role__in=[UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value],
            )
            user.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found or already deleted"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, req, pk, user_id):
        """Update agency user"""
        try:
            user = User.objects.get(id=user_id, agency=pk, deleted_at=None)
            return process_serializer(
                UserSerializer,
                data=req.data,
                success_status=status.HTTP_200_OK,
                original_object=user,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @transaction.atomic
    def post(self, req, pk, user_id):
        """Handle user actions like resend magic link or restore"""
        action = req.data.get('action')
        
        if action == 'resend_magic_link':
            try:
                user = User.objects.get(id=user_id, agency=pk, deleted_at=None)
                user.is_active = False  # Set to Inactive when magic link is sent
                user.save()
                inviting_user = req.user
                user_invitation(req, user, inviting_user)
                return Response(
                    {"message": "Magic link sent successfully"}, 
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif action == 'restore':
            try:
                user = User.objects.get(id=user_id, agency=pk)
                user.restore()
                return Response(
                    {"message": "User restored successfully"}, 
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "Deleted user not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(
            {"error": "Invalid action"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class AgencyReportsAPI(APIView):
    def get(self, req, pk):
        reports = Report.objects.filter(agency=pk)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AgencyBulkActionsAPI(APIView):
    @transaction.atomic
    def post(self, req, pk):
        """Handle bulk actions like resend magic links or restore users"""
        action = req.data.get('action', 'resend_magic_links')  # Default to resend for backward compatibility
        user_ids = req.data.get('user_ids', [])
        
        if not user_ids:
            return Response(
                {"error": "user_ids is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'resend_magic_links':
            users = User.objects.filter(
                id__in=user_ids, 
                agency=pk,
                role__in=[UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value],
                deleted_at=None  # Only send to non-deleted users
            )
            
            if users.count() != len(user_ids):
                return Response(
                    {"error": "Some users not found or already deleted"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            inviting_user = req.user
            success_count = 0
            
            for user in users:
                if user.is_active is True: 
                    continue

                try:
                    user.is_active = False  # Set to Inactive when magic link is sent
                    user.save()
                    
                    # Send notifications to relevant users about the user update
                    send_user_notifications(user)
                    
                    user_invitation(req, user, inviting_user)
                    success_count += 1
                except Exception as e:
                    # Log error but continue with other users
                    print(f"Failed to send magic link to user {user.id}: {str(e)}")
            
            return Response(
                {"message": f"Magic links sent to {success_count} out of {len(user_ids)} users"}, 
                status=status.HTTP_200_OK
            )
        
        elif action == 'restore':
            users = User.objects.filter(
                id__in=user_ids, 
                agency=pk,
                role__in=[UserRole.AGENCY_ADMIN.value, UserRole.AGENCY_USER.value],
            )
            
            if users.count() != len(user_ids):
                return Response(
                    {"error": "Some users not found or not deleted"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            for user in users:
                user.restore()
            
            return Response(
                {"message": f"Successfully restored {len(user_ids)} users"}, 
                status=status.HTTP_200_OK
            )
        
        else:
            return Response(
                {"error": "Invalid action. Supported actions: resend_magic_links, restore"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
