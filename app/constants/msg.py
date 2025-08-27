from typing import Final

MSG_USER_VALIDATION: Final = {
    "password": "Passwords do not match.",
    "credential": "Invalid credentials.",
    "does_not_exist": "The selected user does not exist.",
    "invalid": "Invalid value for user.",
}

MSG_SCHOOL_VALIDATION: Final = {
    "state": "State must be a 2-character abbreviation.",
    "zipcode": "Zipcode must be a 5-digit number.",
    "does_not_exist": "The selected school does not exist.",
    "invalid": "Invalid value for school.",
}

MSG_NOTIFICATION_VALIDATION: Final = {
    "does_not_exist": "The selected notification does not exist.",
    "required": "Title and receiver are required.",
}

MSG_RUBRIC_VALIDATION: Final = {"error": "Rubric Not Found!"}

MSG_AUTH: Final = {"error": "You are not authorized to update this user."}

MSG_USER_DELETED: Final = "User deleted successfully."
MSG_SCHOOL_DELETED: Final = "School Deleted Successfully!"
MSG_REPORT_DELETED: Final = "Report Deleted Successfully!"
MSG_RUBRIC_DELETED: Final = "Rubric Deleted Success"
MSG_AGENCY_DELETED: Final = "Agency Deleted Successfully"
MSG_APPLICATION_DELETED: Final = "Application deleted Successfully!"
MSG_APPLICATION_SECTION_DELETED: Final = "Application Section Deleted Successfully!"
MSG_APPLICATION_SUBSECTION_DELETED: Final = (
    "Application Sub Section Deleted Successfully!"
)
MSG_APPLICATION_QUESTION_DELETED: Final = "Application Question Deleted Successfully!"
MSG_SCHOOL_APPLICATION_DELETD: Final = "School Application Deleted Successfully"
MSG_RUBRIC_SCORE_DELETED: Final = "Rubric Score Deleted Successfully!"
MSG_SUBMISSION_DELETED: Final = "Submission Deleted Successfully!"
MSG_SCHOOL_DOCUMENT_DELETED: Final = "School Document Deleted Successfully!"
MSG_COMPLAINT_DELETED: Final = "Complaint Deleted Successfully!"

MSG_REPORT_ID_REQUIRED: Final = "Report ID is required."
MSG_REPORT_NOT_FOUND: Final = "Report Not Found"

MSG_NORMAL_DELETE: Final = "Deleted Successfully!"

MSG_NOTIFICATION_DELETED: Final = "Notification Deleted Successfully!"
MSG_NOTIFICATION_DELETED_ERROR: Final = "Error Deleting Notification!"
MSG_NOTIFICATINO_MARKED_READ: Final = "Notification Marked as Read Successfully!"
MSG_NOTIFICATION_MARKED_UNREAD: Final = "Notification Marked as Unread Successfully!"
MSG_NOTIFICATION_MARKED_ALL_READ: Final = (
    "All Notifications Marked as Read Successfully!"
)
MSG_NOTIFICATION_MARKED_ALL_UNREAD: Final = (
    "All Notifications Marked as Unread Successfully!"
)
MSG_NOTIFICATION_MARKED_ALL_DELETED: Final = "All Notifications Deleted Successfully!"
MSG_NOTIFICATION_MARKED_ERROR: Final = "Error Marking Notifications!"
MSG_NOTIFICATION_MARKED_READ_ERROR: Final = "Error Marking Notification as Read!"
MSG_NOTIFNOTIFICATION_NOT_FOUND: Final = "Notification Not Found!"

MSG_NOTIFICATION_FETCHED: Final = "Notifications Fetched Successfully!"
MSG_NOTIFICATION_FETCH_ERROR: Final = "Error Fetching Notifications!"


MSG_UNAUTHORIZED_ACCESS: Final = "You are not authorized to access this resource."
