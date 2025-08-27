from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from config.settings import DEFAULT_FROM_EMAIL, SENDGRID_API_KEY


class SendGridService:
    def __init__(self):
        self.api_key = SENDGRID_API_KEY
        self.default_from_email = DEFAULT_FROM_EMAIL
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable not set")
        self.client = SendGridAPIClient(self.api_key)

    def send_email(self, from_email, to_email, subject, content):
        if not from_email:
            from_email = self.default_from_email

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=content,
        )
        try:
            response = self.client.send(message)
            return response.status_code, response.body, response.headers
        except Exception as e:
            print(f"Error sending email: {e}")
            return None


# Example usage:
# sendgrid_service = SendGridService()
# sendgrid_service.send_email('recipient@example.com', 'Test Subject', '<strong>Test Content</strong>')
