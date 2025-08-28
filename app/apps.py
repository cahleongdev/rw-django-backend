from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        """Set up LocalStack resources when the app is ready"""
        try:
            # Import here to avoid circular imports
            from app.services.aws_mock import mock_aws_service
            
            # Set up LocalStack resources if needed
            if mock_aws_service.use_localstack:
                print("Setting up LocalStack resources...")
                mock_aws_service.setup_localstack_resources()
                print("LocalStack resources setup completed")
            else:
                print("Not using LocalStack - AWS credentials found")
        except Exception as e:
            # Don't fail startup if LocalStack setup fails
            print(f"Warning: Could not set up LocalStack resources: {e}")
            import traceback
            traceback.print_exc()
