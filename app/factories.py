import random

import factory
from factory.django import DjangoModelFactory
from faker import Faker

import app.constants.options as OPTION_CONST
from app.models.agencies import Agency
from app.models.applications import (
    Application,
    ApplicationComment,
    ApplicationMessage,
    ApplicationSchool,
    ApplicationSection,
)
from app.models.complaints import Complaint
from app.models.frameworks import Framework, FrameworkSection, RateFramework
from app.models.messages import Message
from app.models.notifications import Notification
from app.models.reports import Report
from app.models.rubrics import Rubric, Score
from app.models.schools import School, SchoolDocument
from app.models.submissions import Submission, SubmissionMessage
from app.models.users import User
from app.utils.helper import generateUniqueID

# Initialize Faker
fake = Faker()


# Helper Function to Generate Limited Random Strings
def limited_random_string(max_length=15):
    return fake.text(max_length=max_length).strip()


# Agency Factory
class AgencyFactory(DjangoModelFactory):
    class Meta:
        model = Agency
        django_get_or_create = [
            "agency_title"
        ]  # Prevent duplication based on `agency_title`

    agency_title = factory.Sequence(lambda n: f"Agency {n + 1}")
    admin_privileges = factory.LazyAttribute(
        lambda _: random.choices(
            ["Dashboard", "School", "Report", "Submission", "Application"]
        )
    )
    school_privileges = factory.LazyAttribute(
        lambda _: random.choices(
            ["Dashboard", "School", "Report", "Submission", "Application"]
        )
    )
    access_school = factory.LazyAttribute(lambda _: random.choice([True, False]))
    home_url = factory.LazyAttribute(lambda _: fake.url())


# School Factory
class SchoolFactory(DjangoModelFactory):
    class Meta:
        model = School

    id = factory.LazyFunction(generateUniqueID)
    name = factory.LazyAttribute(lambda _: f"{fake.company()} School")
    agency = factory.LazyAttribute(lambda _: random.choice(Agency.objects.all()))
    gradeserved = [1, 2, 3, 4, 5, 6, 7, 8]
    county = "USA"
    city = factory.LazyAttribute(lambda _: fake.city())
    state = factory.LazyAttribute(lambda _: fake.state_abbr())
    zipcode = factory.LazyAttribute(lambda _: fake.zipcode())
    district = factory.LazyAttribute(lambda _: fake.address())
    address = factory.LazyAttribute(lambda _: fake.address())
    type = factory.LazyAttribute(
        lambda _: random.choice(OPTION_CONST.SCHOOL_TYPE_CHOICES)
    )
    creator = factory.LazyAttribute(lambda _: fake.email())


# User Factory
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    id = factory.LazyFunction(generateUniqueID)
    first_name = factory.LazyAttribute(lambda _: fake.first_name()[:15])
    last_name = factory.LazyAttribute(lambda _: fake.last_name()[:15])
    email = factory.LazyAttribute(lambda _: fake.email())
    title = factory.LazyAttribute(lambda _: fake.job()[:15])
    phone_number = factory.LazyAttribute(lambda _: fake.numerify("###-###-####"))
    profile_image = factory.LazyAttribute(lambda _: fake.image_url()[:15])
    role = factory.LazyAttribute(
        lambda _: random.choice(["School_User", "School_Admin", "Board_Member"])
    )
    school = factory.LazyAttribute(lambda _: random.choice(School.objects.all()))
    password = factory.PostGenerationMethodCall("set_password", "password123")


# Report Factory
class ReportFactory(DjangoModelFactory):
    class Meta:
        model = Report

    id = factory.LazyFunction(generateUniqueID)
    name = factory.LazyAttribute(lambda _: fake.catch_phrase() + " Report")
    description = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))
    due_date = factory.LazyAttribute(lambda _: fake.future_datetime())
    completion_time = factory.LazyAttribute(lambda _: fake.random_number())
    domain = factory.LazyAttribute(lambda _: fake.domain_name())
    agency = factory.LazyAttribute(lambda _: random.choice(Agency.objects.all()))
    type = factory.LazyAttribute(
        lambda _: random.choice(OPTION_CONST.REPORT_TYPE_CHOICES)
    )
    submission_format = factory.LazyAttribute(lambda _: fake.file_extension())


# Submission Factory
class SubmissionFactory(DjangoModelFactory):
    class Meta:
        model = Submission

    id = factory.LazyFunction(generateUniqueID)
    school = factory.LazyAttribute(lambda _: random.choice(School.objects.all()))
    report = factory.LazyAttribute(lambda _: random.choice(Report.objects.all()))
    assigned_member = factory.LazyAttribute(lambda _: random.choice(User.objects.all()))
    status = factory.LazyAttribute(
        lambda _: random.choice(["pending", "completed", "returned", "incompleted"])
    )
    due_date = factory.LazyAttribute(lambda _: fake.future_datetime())
    school_submission_date = factory.LazyAttribute(lambda _: fake.future_datetime())
    evaluator_submission_date = factory.LazyAttribute(lambda _: fake.future_datetime())
    file_urls = factory.LazyAttribute(lambda _: fake.url())


# Rubric Factory
class RubricFactory(DjangoModelFactory):
    class Meta:
        model = Rubric

    id = factory.LazyFunction(generateUniqueID)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=2))


# Framework Factory
class FrameworkFactory(DjangoModelFactory):
    class Meta:
        model = Framework

    id = factory.LazyFunction(generateUniqueID)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=5))
    description = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=2))


# Complaint Factory
class ComplaintFactory(DjangoModelFactory):
    class Meta:
        model = Complaint

    id = factory.LazyFunction(generateUniqueID)
    email = factory.LazyAttribute(lambda _: fake.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name()[:15])
    last_name = factory.LazyAttribute(lambda _: fake.last_name()[:15])
    phone_number = factory.LazyAttribute(lambda _: fake.numerify("##########")[:15])
    status = factory.LazyAttribute(
        lambda _: random.choice(["open", "closed", "pending"])
    )


# Application Factory
class ApplicationFactory(DjangoModelFactory):
    class Meta:
        model = Application

    id = factory.LazyFunction(generateUniqueID)
    name = factory.LazyAttribute(lambda _: fake.catch_phrase())
    description = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=2))
    agency = factory.LazyAttribute(lambda _: random.choice(Agency.objects.all()))
    due_date = factory.LazyAttribute(lambda _: fake.future_datetime())


# Create a set to track used combinations
used_combinations = set()


class ApplicationSchoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApplicationSchool

    @factory.lazy_attribute
    def application(self):
        # Ensure application is selected randomly
        return random.choice(Application.objects.all())

    @factory.lazy_attribute
    def school(self):
        # Ensure school is selected randomly and unique combination is enforced
        all_schools = School.objects.all()
        for _ in range(len(all_schools)):
            school = random.choice(all_schools)
            if (self.application, school) not in used_combinations:
                used_combinations.add((self.application, school))
                return school
        raise ValueError(
            "No unique combinations available between applications and schools."
        )

    status = factory.Faker("random_element", elements=["completed", "incompleted"])
    submission_time = factory.Faker("date_time_this_year")
    due_date = factory.Faker("date_time_this_year", after_now=True)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    id = factory.LazyFunction(generateUniqueID)
    sender = factory.LazyAttribute(lambda _: random.choice(User.objects.all()))
    receiver = factory.LazyAttribute(lambda _: random.choice(User.objects.all()))
    message = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=2))
    created_at = factory.LazyAttribute(lambda _: fake.future_datetime())


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    id = factory.LazyFunction(generateUniqueID)
    receiver = factory.LazyAttribute(lambda _: random.choice(User.objects.all()))
    message = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=2))
    type = factory.LazyAttribute(lambda _: random.choice(["info", "warning", "error"]))
    created_at = factory.LazyAttribute(lambda _: fake.future_datetime())


class SchoolDocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SchoolDocument

    id = factory.LazyFunction(generateUniqueID)
    file_url = factory.LazyAttribute(lambda _: fake.url())
    school = factory.LazyAttribute(lambda _: random.choice(School.objects.all()))
    type = factory.LazyAttribute(lambda _: fake.file_extension())
    name = factory.LazyAttribute(lambda _: fake.file_name())
    year = factory.LazyAttribute(lambda _: fake.year())
    created_by = factory.LazyAttribute(lambda _: fake.email())
