import random
import time
import pyotp
import math
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.db.models import JSONField

from app.models.agencies import Agency
from app.models.documents import Document
from app.models.schools import School


class User(AbstractUser):

    id = models.CharField(max_length=50, primary_key=True)
    email = models.CharField(max_length=100, unique=True, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.URLField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=20, default="Member")
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    schools = models.ManyToManyField(School, blank=True, related_name="users")
    notification_settings = models.JSONField(default=dict)
    custom_fields = models.JSONField(default=dict)
    permissions = models.JSONField(default=dict)
    documents = GenericRelation(Document)

    # Override is_active to support three states: null (Pending), False (Inactive), True (Active)
    is_active = models.BooleanField(default=None, null=True, blank=True)

    # Marketing consent field for GDPR compliance
    receive_marketing = models.BooleanField(default=False)

    # Soft delete field - using only deleted_at (null = active, not null = deleted)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Password reset fields
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    reset_token_expires_at = models.DateTimeField(null=True, blank=True)
    reset_token_method = models.CharField(max_length=10, null=True, blank=True)  # 'sms' or 'email'
    reset_token_used = models.BooleanField(default=False)

    # Invitation fields
    invitation_token = models.CharField(max_length=255, null=True, blank=True)
    invitated_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    invitation_token_expires_at = models.DateTimeField(null=True, blank=True)

    # MFA fields
    mfa_secret = models.CharField(max_length=32, null=True, blank=True)
    mfa_method = models.JSONField(default=list)  # List of enabled MFA methods, e.g., ['totp', 'sms']
    mfa_enabled = models.BooleanField(default=False)
    mfa_backup_codes = JSONField(default=list)  # List of one-time backup codes
    mfa_phone = models.CharField(max_length=15, null=True, blank=True)  # Phone number for SMS MFA
    mfa_email = models.CharField(max_length=100, null=True, blank=True)  # Email for email-based MFA
    mfa_temp_code = models.CharField(max_length=6, null=True, blank=True)  # Temporary code for SMS/Email verification
    mfa_temp_code_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{int(time.time() * 1000)}x{random.randint(100000000000000, 999999999999999)}"
        super().save(*args, **kwargs)

    def is_reset_token_expired(self):
        if not self.reset_token_expires_at:
            return True
        return timezone.now() > self.reset_token_expires_at

    def is_invitation_token_expired(self):
        if not self.invitation_token_expires_at:
            return True
        return timezone.now() > self.invitation_token_expires_at

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expires_at = None
        self.reset_token_method = None
        self.reset_token_used = False
        self.save()

    def clear_invitation_token(self):
        self.invitation_token = None
        self.invitation_token_expires_at = None
        self.invitation_token_method = None
        self.save()

    def generate_mfa_secret(self):
        """Generate a new MFA secret key"""
        self.mfa_secret = pyotp.random_base32()
        self.save()
        return self.mfa_secret

    def verify_totp_code(self, code):
        """Verify a TOTP code"""
        if not self.mfa_secret:
            return False
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(code)

    def get_totp_uri(self):
        """Get the TOTP URI for QR code generation"""
        if not self.mfa_secret:
            self.generate_mfa_secret()
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.provisioning_uri(self.email, issuer_name="ReportWell")

    def generate_backup_codes(self, count=8):
        """Generate new backup codes"""
        codes = []
        for _ in range(count):
            first_part = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=math.floor(count/2)))
            second_part = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=math.ceil(count/2)))
            code = f"{first_part}-{second_part}"
            codes.append(code)
        self.mfa_backup_codes = codes
        self.save()
        return codes

    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if code in self.mfa_backup_codes:
            self.mfa_backup_codes.remove(code)
            self.save()
            return True
        return False

    def generate_temp_code(self):
        """Generate a temporary code for SMS/Email verification"""
        code = ''.join(random.choices('0123456789', k=6))
        self.mfa_temp_code = code
        self.mfa_temp_code_expires_at = timezone.now() + timezone.timedelta(seconds=60)
        self.save()
        return code

    def verify_temp_code(self, code):
        """Verify a temporary code for SMS/Email verification"""
        if not self.mfa_temp_code or not self.mfa_temp_code_expires_at:
            return False
        if timezone.now() > self.mfa_temp_code_expires_at:
            return False
        if code != self.mfa_temp_code:
            return False
        self.mfa_temp_code = None
        self.mfa_temp_code_expires_at = None
        self.save()
        return True

    def soft_delete(self):
        """Soft delete the user"""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft deleted user"""
        self.deleted_at = None
        self.save()

    @classmethod
    def active_objects(cls):
        """Return only non-deleted users"""
        return cls.objects.filter(deleted_at=None)

    @classmethod
    def deleted_objects(cls):
        """Return only soft deleted users"""
        return cls.objects.filter(deleted_at__isnull=False)
