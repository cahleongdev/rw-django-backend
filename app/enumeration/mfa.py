from .base_enum import BaseEnum


class MFAMethod(str, BaseEnum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"
    BACKUP_CODE = "backup_code"


class PhoneVerificationMethod(str, BaseEnum):
    SMS = "sms"
    VOICE = "voice"
