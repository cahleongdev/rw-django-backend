import base64
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import urlparse

import qrcode
import qrcode.image.svg
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from app.enumeration.mfa import MFAMethod, PhoneVerificationMethod
from app.enumeration.notification_type import NotificationType
from app.models.notifications import Notification
from app.serializers.auth import (
    AcceptInviteSerializer,
    ContactInfoSerializer,
    GenerateTOTPSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    SendMFACodeSerializer,
    SendResetLinkSerializer,
    ValidateInviteTokenSerializer,
    VerifyTOTPSerializer,
    ChangePasswordSerializer,
)
from app.serializers.users import UserSerializer
from app.services.users import generate_token_code, send_invitation_email
from app.services.sendgrid import SendGridService
from app.services.twilio import TwilioService
from app.serializers.auth import CustomTokenRefreshSerializer

User = get_user_model()


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            201: UserSerializer,
            400: "Bad request",
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # Check if user has MFA enabled
        if user.mfa_enabled and user.mfa_method:
            # Store user ID in session for MFA verification
            request.session["pending_user_id"] = user.id
            request.session["login_timestamp"] = timezone.now().isoformat()

            return Response(
                {
                    "mfa_required": True,
                    "mfa_methods": user.mfa_method,
                    "message": "MFA verification required",
                },
                status=status.HTTP_200_OK,
            )

        # If no MFA required, proceed with normal login
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        access_token["user_id"] = user.id
        access_token["email"] = user.email
        access_token["role"] = user.role
        access_token["schools"] = None
        access_token["agency"] = None

        if user.schools.exists():
            access_token["schools"] = list(user.schools.values_list("id", flat=True))
        if user.agency is not None:
            access_token["agency"] = user.agency.id

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(access_token),
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginMFAVerifyAPI(APIView):
    """Verify MFA code during login process"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body={
            "type": "object",
            "properties": {"code": {"type": "string"}, "method": {"type": "string"}},
        },
        responses={
            200: "MFA verification successful, login complete",
            400: "Invalid code or session expired",
        },
    )
    def post(self, request):
        code = request.data.get("code")
        method = request.data.get("method")

        if not code or not method:
            return Response(
                {"error": "Code and method are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get pending user from session
        pending_user_id = request.session.get("pending_user_id")
        login_timestamp = request.session.get("login_timestamp")

        if not pending_user_id or not login_timestamp:
            return Response(
                {"error": "No pending login session found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if session is still valid (5 minutes)
        login_time = datetime.fromisoformat(login_timestamp)
        if timezone.now() - login_time > timedelta(minutes=5):
            # Clear expired session
            request.session.pop("pending_user_id", None)
            request.session.pop("login_timestamp", None)
            return Response(
                {"error": "Login session expired. Please login again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=pending_user_id, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid session"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Verify MFA code based on method
        verification_successful = False

        if method == MFAMethod.TOTP.value:
            verification_successful = user.verify_totp_code(code)
        elif method in [
            MFAMethod.SMS.value,
            MFAMethod.EMAIL.value,
            MFAMethod.VOICE.value,
        ]:
            verification_successful = user.verify_temp_code(code)
        elif method == MFAMethod.BACKUP_CODE.value:
            verification_successful = user.verify_backup_code(code)

        if not verification_successful:
            return Response(
                {"error": "Invalid verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clear session data
        request.session.pop("pending_user_id", None)
        request.session.pop("login_timestamp", None)

        # Generate tokens for successful login
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        access_token["user_id"] = user.id
        access_token["email"] = user.email
        access_token["role"] = user.role
        access_token["schools"] = None
        access_token["agency"] = None

        if user.schools.exists():
            access_token["schools"] = list(user.schools.values_list("id", flat=True))
        if user.agency is not None:
            access_token["agency"] = user.agency.id

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(access_token),
                "message": "Login successful",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginMFASendCodeAPI(APIView):
    """Send MFA code during login process"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body={"type": "object", "properties": {"method": {"type": "string"}}},
        responses={
            200: "Code sent successfully",
            400: "Bad request",
        },
    )
    def post(self, request):
        method = request.data.get("method")

        if not method:
            return Response(
                {"error": "Method is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get pending user from session
        pending_user_id = request.session.get("pending_user_id")

        if not pending_user_id:
            return Response(
                {"error": "No pending login session found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=pending_user_id, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid session"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Generate and send code based on method
        if method in [
            MFAMethod.SMS.value,
            MFAMethod.EMAIL.value,
            MFAMethod.VOICE.value,
        ]:
            code = user.generate_temp_code()

            if method in [MFAMethod.SMS.value, MFAMethod.VOICE.value]:
                phone = user.mfa_phone if user.mfa_phone else user.phone_number
                if not phone:
                    return Response(
                        {"error": "Phone number not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                twilio_service = TwilioService()

                if method == MFAMethod.SMS.value:
                    message = f"Your ReportWell verification code is: {code}"
                    twilio_service.send_sms(to=phone, from_=None, body=message)
                else:  # VOICE
                    message = f'Your ReportWell verification code is: {" ".join(code)}. I repeat, your code is: {" ".join(code)}'
                    twiml = f"""
                        <?xml version="1.0" encoding="UTF-8"?>
                        <Response>
                            <Say voice="alice">{message}</Say>
                            <Pause length="2"/>
                            <Say voice="alice">{message}</Say>
                        </Response>
                    """
                    twilio_service.make_call(to=phone, twiml=twiml, from_=None)

            elif method == MFAMethod.EMAIL.value:
                email = user.mfa_email if user.mfa_email else user.email
                sendgrid_service = SendGridService()
                content = f"""
                    <h2>ReportWell Login Verification</h2>
                    <p>Your verification code is: {code}</p>
                    <p>This code will expire in 60 seconds.</p>
                """
                sendgrid_service.send_email(
                    to_email=email,
                    from_email=None,
                    subject="ReportWell Login Verification Code",
                    content=content,
                )

            return Response(
                {"message": f"Verification code sent via {method}"},
                status=status.HTTP_200_OK,
            )

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPI(APIView):
    def get(self, req):
        token_data = getattr(req, "token_data", None)
        user_id = token_data["user_id"]
        currentUser = get_object_or_404(User, pk=user_id)
        serializer = UserSerializer(currentUser)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: "Password changed successfully",
            400: "Bad request",
        },
    )
    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["newPassword"])
        user.save()
        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class GetContactInfoAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: ContactInfoSerializer,
            404: "User not found",
        },
    )
    def get(self, request, email):
        try:
            user = User.objects.get(email=email, deleted_at__isnull=True)
            serializer = ContactInfoSerializer(
                {"email": user.email, "phone": user.phone_number}
            )
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SendResetLinkAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendResetLinkSerializer

    @swagger_auto_schema(
        request_body=SendResetLinkSerializer,
        responses={
            200: "Reset link sent successfully",
            400: "Bad request",
            404: "User not found",
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data["email"]
        method = data["method"]

        try:
            user = User.objects.get(email=email, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate reset token
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        user.reset_token = token
        user.reset_token_expires_at = timezone.now() + timedelta(hours=24)
        user.reset_token_method = method
        user.reset_token_used = False
        user.save()

        # Get frontend URL from request
        referer = request.META.get("HTTP_REFERER", "")
        if referer:
            parsed_url = urlparse(referer)
            frontend_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            frontend_url = request.build_absolute_uri("/")[:-1]

        reset_url = f"{frontend_url}/reset-password?token={token}"

        # Send reset link based on method
        if method == "email":
            sendgrid_service = SendGridService()
            email_content = f"""
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>This link will expire in 24 hours.</p>
            """
            sendgrid_service.send_email(
                from_email=None,
                to_email=user.email,
                subject="Password Reset Request",
                content=email_content,
            )
        elif method == "sms":
            if not user.phone_number:
                return Response(
                    {"error": "Phone number not found for this user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            twilio_service = TwilioService()
            sms_content = f"Click the link to reset your password: {reset_url}"
            twilio_service.send_sms(to=user.phone_number, from_=None, body=sms_content)

        return Response(
            {"message": "Password reset link has been sent"}, status=status.HTTP_200_OK
        )


class ValidateResetTokenAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: "Token is valid",
            400: "Invalid or expired token",
        },
    )
    def get(self, request, token):
        try:
            user = User.objects.get(
                reset_token=token, reset_token_used=False, deleted_at__isnull=True
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid or expired reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_reset_token_expired():
            return Response(
                {"error": "Reset token has expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)


class ResetPasswordAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={
            200: "Password reset successful",
            400: "Invalid token or passwords don't match",
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token = data["token"]
        new_password = data["newPassword"]

        try:
            user = User.objects.get(
                reset_token=token, reset_token_used=False, deleted_at__isnull=True
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid or expired reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_reset_token_expired():
            return Response(
                {"error": "Reset token has expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        user.set_password(new_password)
        user.clear_reset_token()
        user.save()

        return Response(
            {"message": "Password has been reset successfully"},
            status=status.HTTP_200_OK,
        )


class ValidateInviteTokenAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ValidateInviteTokenSerializer

    @swagger_auto_schema(
        responses={
            200: ValidateInviteTokenSerializer,
            400: "Invalid or expired token",
        },
    )
    def get(self, request, token):
        try:
            user = User.objects.get(invitation_token=token, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid invitation token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if invitation was already used (user is already registered)
        if user.is_active:
            return Response(
                {
                    "error": "already_registered",
                    "message": "This email is already registered",
                    "email": user.email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if invitation token has expired
        if user.is_invitation_token_expired():
            return Response(
                {
                    "error": "expired",
                    "message": "Invitation token has expired",
                    "email": user.email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(user)
        return Response(serializer.data)


class AcceptInviteAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AcceptInviteSerializer

    @swagger_auto_schema(
        request_body=AcceptInviteSerializer,
        responses={
            200: "Invitation accepted successfully",
            400: "Invalid token or password requirements not met",
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token = data["token"]
        password = data["password"]

        try:
            user = User.objects.get(
                invitation_token=token,
                deleted_at__isnull=True,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Invalid or expired invitation token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_invitation_token_expired():
            return Response(
                {"error": "Invitation token has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user
        user.email = data["email"]
        user.username = data["email"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.phone_number = data["phone"]
        user.title = data["title"]
        user.custom_fields = data["custom_fields"]
        user.receive_marketing = data.get("receive_marketing", False)
        user.set_password(password)
        user.is_active = True
        user.clear_invitation_token()
        user.save()

        return Response(
            {"message": "Invitation accepted successfully"}, status=status.HTTP_200_OK
        )


class RequestNewMagicLinkAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body={
            "type": "object",
            "properties": {"email": {"type": "string", "format": "email"}},
            "required": ["email"],
        },
        responses={
            200: "New magic link sent successfully",
            400: "Bad request",
            404: "User not found or not eligible for new link",
        },
    )
    def post(self, request):
        user_id = request.data.get("userId")

        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find user with this email who has an invitation token (used or unused)
            user = User.objects.get(
                id=user_id, invitation_token__isnull=False, deleted_at__isnull=True
            )
        except User.DoesNotExist:
            return Response(
                {"error": "No pending invitation found for this user"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user is already active (invitation already accepted)
        if user.is_active:
            return Response(
                {"error": "This user is already registered. Please sign in instead."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the original inviting user
        inviting_user = user.invitated_by
        if not inviting_user:
            return Response(
                {"error": "Unable to resend invitation. Please contact support."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate new token and send email
        new_token = generate_token_code(user, inviting_user)
        send_invitation_email(request, user, inviting_user, new_token)

        return Response(
            {"message": "A new magic link has been sent to your email"},
            status=status.HTTP_200_OK,
        )


class GenerateTOTPAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateTOTPSerializer

    @swagger_auto_schema(
        request_body=GenerateTOTPSerializer,
        responses={
            200: "TOTP secret and QR code",
            400: "Bad request",
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        method = serializer.validated_data["method"]

        if method == MFAMethod.TOTP.value:
            # Generate TOTP secret and QR code
            secret = user.generate_mfa_secret()
            uri = user.get_totp_uri()

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=3,
            )
            qr.add_data(uri)
            qr.make(fit=True)

            # Create SVG QR code
            img = qr.make_image(image_factory=qrcode.image.svg.SvgPathFillImage)
            stream = BytesIO()
            img.save(stream)
            qr_code = base64.b64encode(stream.getvalue()).decode()

            return Response({"secret": secret, "qr_code": qr_code})

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyTOTPAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyTOTPSerializer

    @swagger_auto_schema(
        request_body=VerifyTOTPSerializer,
        responses={
            200: "Verification successful",
            400: "Invalid code",
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = serializer.validated_data["code"]
        method = serializer.validated_data["method"]

        if method == MFAMethod.TOTP.value:
            if user.verify_totp_code(code):
                user.mfa_enabled = True
                if user.mfa_method is None:
                    user.mfa_method = []
                user.mfa_method.append(MFAMethod.TOTP.value)
                user.save()

                # Generate backup codes
                backup_codes = user.generate_backup_codes()

                return Response(
                    {
                        "message": "Verification successful",
                        "backup_codes": backup_codes,
                        "mfa_method": user.mfa_method,
                    }
                )
            return Response(
                {"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
            )

        elif method in [
            MFAMethod.SMS.value,
            MFAMethod.EMAIL.value,
            MFAMethod.VOICE.value,
        ]:
            if user.verify_temp_code(code):
                user.mfa_enabled = True
                if user.mfa_method is None:
                    user.mfa_method = []
                user.mfa_method.append(method)
                user.save()

                # Generate backup codes
                backup_codes = user.generate_backup_codes()

                return Response(
                    {
                        "message": f"{method.upper()} verification successful",
                        "backup_codes": backup_codes,
                        "mfa_method": user.mfa_method,
                    }
                )
            return Response(
                {"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST
            )


class SendMFACodeAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SendMFACodeSerializer

    @swagger_auto_schema(
        request_body=SendMFACodeSerializer,
        responses={
            200: "Code sent successfully",
            400: "Bad request",
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        method = serializer.validated_data["method"]
        code = user.generate_temp_code()

        if method in [MFAMethod.SMS.value, MFAMethod.VOICE.value]:
            phone = serializer.validated_data.get("phone")
            if not phone:
                phone = (
                    user.mfa_phone
                    if user.mfa_phone
                    else user.phone_number if user.phone_number else None
                )
            else:
                user.mfa_phone = phone
                user.save()

            if phone is None:
                return Response(
                    {"error": "Phone number not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            twilio_service = TwilioService()

            if method == PhoneVerificationMethod.SMS.value:
                # Send SMS
                message = f"Your ReportWell verification code is: {code}"
                twilio_service.send_sms(to=phone, from_=None, body=message)
            else:  # VOICE
                # Make voice call

                message = f'Your ReportWell verification code is: {" ".join(code)}. I repeat, your code is: {" ".join(code)}'

                twiml = f"""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <Response>
                        <Say voice="alice">{message}</Say>
                        <Pause length="2"/>
                        <Say voice="alice">{message}</Say>
                    </Response>
                """
                twilio_service.make_call(to=phone, twiml=twiml, from_=None)

        elif method == MFAMethod.EMAIL.value:
            email = serializer.validated_data.get("email")
            if not email:
                email = user.mfa_email
            else:
                user.mfa_email = email
                user.save()

            # Send Email
            sendgrid_service = SendGridService()
            content = f"""
                <h2>ReportWell MFA Verification</h2>
                <p>Your verification code is: {code}</p>
                <p>This code will expire in 60 seconds.</p>
            """
            sendgrid_service.send_email(
                to_email=email,
                from_email=None,
                subject="ReportWell MFA Verification Code",
                content=content,
            )

        return Response(
            {"message": f"Verification code sent via {method}", "method": method}
        )


class VerifyBackupCodeAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body={"code": "string"},
        responses={
            200: "Backup code verified successfully",
            400: "Invalid code",
        },
    )
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"error": "Code is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if user.verify_backup_code(code):
            return Response({"message": "Backup code verified successfully"})

        return Response(
            {"error": "Invalid backup code"}, status=status.HTTP_400_BAD_REQUEST
        )


class GenerateBackupCodesAPI(APIView):
    """Generate new backup codes for MFA"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body={"code": "string"},
        responses={
            200: "Backup codes generated successfully",
            400: "Failed to generate backup codes",
        },
    )
    def post(self, request):
        try:
            # Generate new backup codes
            backup_codes = request.user.generate_backup_codes()

            return Response(
                {
                    "message": "Backup codes generated successfully",
                    "backup_codes": backup_codes,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "Failed to generate backup codes"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RemoveMFAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body={"method": "string"},
        responses={
            200: "MFA removed successfully",
            400: "Bad request",
        },
    )
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return Response(
                {"error": "Method is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if method == MFAMethod.TOTP.value:
            user.mfa_method = [m for m in user.mfa_method if m != MFAMethod.TOTP.value]
        elif method == MFAMethod.SMS.value:
            user.mfa_method = [
                m
                for m in user.mfa_method
                if (m != MFAMethod.SMS.value and m != MFAMethod.VOICE.value)
            ]
        elif method == MFAMethod.EMAIL.value:
            user.mfa_method = [m for m in user.mfa_method if m != MFAMethod.EMAIL.value]

        user.save()
        return Response(
            {"message": "MFA removed successfully", "mfa_method": user.mfa_method}
        )


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
