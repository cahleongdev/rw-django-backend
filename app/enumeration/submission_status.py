from .base_enum import BaseEnum


class SubmissionStatus(BaseEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    RETURNED = "returned"
    INCOMPLETED = "incompleted"
