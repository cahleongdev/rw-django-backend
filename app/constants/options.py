from typing import Final

APPLICATION_STATUS_FIELD_VALUE: Final = {
    "finalized": "Finalized",
    "evaluation": "Evaluation",
    "review": "Review",
    "returned": "Returned",
    "incompleted": "Incompleted",
}

APPLICATION_STATUS_FIELDS: Final = [
    "finalized",
    "evaluation",
    "review",
    "returned",
    "incompleted",
]

APPLICATION_STATUS_OPTIONS = [
    ("finalized", "Finalized"),
    ("evaluation", "Evaluation"),
    ("review", "Review"),
    ("returned", "Returned"),
    ("incompleted", "Incompleted"),
]

SCHOOL_TYPE_CHOICES: Final = [
    "Public",
    "Private",
    "Elementary School",
    "Middle School",
    "High School",
]

REPORT_TYPE_CHOICES: Final = [
    ("Other", "Other"),
    ("State", "State"),
    ("Local", "Local"),
]
REPORT_DOMAIN_CHOICES: Final = [()]

SUBMISSION_STATUS_CHOICES: Final = ["pending", "completed", "returned", "incompleted"]

APPLICATION_SUBSECTION_QUESTION_TYPES = [
    ("short_text", "Short Text"),
    ("long_text", "Long Text"),
    ("single_choice", "Single Choice"),
    ("multiple_choide", "Multiple Choice"),
    ("upload", "Upload"),
]

NOTIFICATION_TYPE_CHOICES: Final = ["info", "warning", "error", "success", "question"]

NOTIFICATION_RECEIVER_CHOICES: Final = ["agency", "school", "user", "all"]
