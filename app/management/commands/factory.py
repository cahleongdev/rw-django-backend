from django.core.management.base import BaseCommand

from app.factories import (
    AgencyFactory,
    ApplicationFactory,
    ApplicationSchoolFactory,
    ComplaintFactory,
    FrameworkFactory,
    MessageFactory,
    ReportFactory,
    RubricFactory,
    SchoolFactory,
    SubmissionFactory,
    UserFactory,
)
from app.models.agencies import Agency


class Command(BaseCommand):
    help = "Generate fake data for all models"

    def handle(self, *args, **kwargs):
        # self.stdout.write("Seeding database with fake data...")

        # # Step 3: Create users linked to agencies
        # for _ in range(30):
        #     UserFactory()

        # self.stdout.write(self.style.SUCCESS("Created 20 users successfully!"))

        # # Step 4: Create reports linked to agencies
        # for _ in range(15):
        #     ReportFactory()

        # self.stdout.write(self.style.SUCCESS("Created 15 reports successfully!"))

        # # Step 5: Create submissions linked to reports and schools
        # for _ in range(20):
        #     SubmissionFactory()

        # self.stdout.write(self.style.SUCCESS("Created 15 submissions successfully!"))

        # # Step 6: Create rubrics and frameworks
        # RubricFactory.create_batch(5)
        # FrameworkFactory.create_batch(5)

        # self.stdout.write(
        #     self.style.SUCCESS("Created 5 rubrics and 5 frameworks successfully!")
        # )

        # # Step 7: Create complaints linked to agencies
        # for _ in range(5):
        #     ComplaintFactory()

        # self.stdout.write(self.style.SUCCESS("Created 5 complaints successfully!"))

        # # Step 8: Create applications linked to agencies
        # for _ in range(7):
        #     ApplicationFactory()

        # self.stdout.write(self.style.SUCCESS("Created 7 applications successfully!"))

        # self.stdout.write(
        #     self.style.SUCCESS("Database seeding completed successfully!")
        # )

        # for _ in range(20):
        #     ApplicationSchoolFactory()

        for _ in range(30):
            MessageFactory()

        self.stdout.write(self.style.SUCCESS("Message seeding completed successfully!"))
