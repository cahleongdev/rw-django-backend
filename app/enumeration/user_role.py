from app.enumeration.base_enum import BaseEnum


class UserRole(BaseEnum):
    SCHOOL_USER = "School_User"
    SCHOOL_ADMIN = "School_Admin"
    AGENCY_USER = "Agency_User"
    AGENCY_ADMIN = "Agency_Admin"
    SUPER_ADMIN = "Super_Admin"
    VIEWER = "Viewer"