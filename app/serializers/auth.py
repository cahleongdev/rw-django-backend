from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

import app.constants.msg as MSG_CONST
from app.models.users import User
from app.utils.helper import mask_phone, mask_email
from app.enumeration.mfa import MFAMethod, PhoneVerificationMethod

User = get_user_model()


# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if user and user.is_active:
            return user
        raise serializers.ValidationError(MSG_CONST.MSG_USER_VALIDATION["credential"])
    
# Custom Token Refresh Serializer
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])

        user_id = refresh['user_id']
        user = User.objects.get(id=user_id, deleted_at__isnull=True)
        if not user:
            raise serializers.ValidationError(MSG_CONST.MSG_USER_DELETED)

        access_token = refresh.access_token

        access_token['user_id'] = user.id
        access_token['email'] = user.email
        access_token['role'] = user.role
        access_token['schools'] = None
        access_token['agency'] = None

        if hasattr(user, 'schools') and user.schools.exists():
            access_token['schools'] = list(user.schools.values_list('id', flat=True))
        if hasattr(user, 'agency') and user.agency is not None:
            access_token['agency'] = user.agency.id
        data['access'] = str(access_token)
        
        return data


# Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True, min_length=8)

    def validate_currentPassword(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

class ContactInfoSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def get_email(self, obj):
        return mask_email(obj['email'])

    def get_phone(self, obj):
        return mask_phone(obj['phone'])


class SendResetLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()
    method = serializers.ChoiceField(choices=['sms', 'email'])


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    newPassword = serializers.CharField(min_length=8)


class ValidateInviteTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    custom_fields = serializers.DictField(required=False)
    receive_marketing = serializers.BooleanField(required=False, default=False)


class AcceptInviteSerializer(serializers.Serializer):
    token = serializers.CharField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8)
    custom_fields = serializers.DictField(required=False)
    receive_marketing = serializers.BooleanField(required=False, default=False)

class GenerateTOTPSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=MFAMethod.choices())

class VerifyTOTPSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)
    method = serializers.ChoiceField(choices=MFAMethod.choices())

class SendMFACodeSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=MFAMethod.choices())
    phone = serializers.CharField(required=False, allow_blank=True)
    phone_method = serializers.ChoiceField(choices=PhoneVerificationMethod.choices(), required=False)
    email = serializers.CharField(required=False, allow_blank=True)

class BackupCodesSerializer(serializers.Serializer):
    codes = serializers.ListField(child=serializers.CharField())