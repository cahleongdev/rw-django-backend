from django.core.management.base import BaseCommand
from app.services.aws_mock import mock_aws_service


class Command(BaseCommand):
    help = "Set up LocalStack resources (DynamoDB tables, S3 buckets)"

    def handle(self, *args, **options):
        self.stdout.write("Setting up LocalStack resources...")
        
        try:
            mock_aws_service.setup_localstack_resources()
            self.stdout.write(
                self.style.SUCCESS("LocalStack resources set up successfully!")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to set up LocalStack resources: {e}")
            )
            self.stdout.write(
                "Make sure LocalStack is running and accessible at the configured endpoint."
            )
