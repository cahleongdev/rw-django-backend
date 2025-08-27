from twilio.rest import Client
from config.settings import TWILIO_ACCOUNT_SID, TWILIO_API_KEY, TWILIO_PHONE_NUMBER

class TwilioService:
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.api_key = TWILIO_API_KEY
        
        self.client = Client(self.account_sid, self.api_key)

    def send_sms(self, to, from_, body):
        if not from_:
            from_ = TWILIO_PHONE_NUMBER

        message = self.client.messages.create(
            body=body,
            from_=from_,
            to=to
        )

    def make_call(self, from_, to: str, twiml: str) -> None:
        """
        Make a voice call using Twilio.
        
        Args:
            to (str): The recipient's phone number
            message (str): The message to be spoken
        """
        if not from_:
            from_ = TWILIO_PHONE_NUMBER
        
        self.client.calls.create(
            twiml=twiml,
            from_=from_,
            to=to
        )


# Example usage:
# twilio_service = TwilioService()
# twilio_service.send_sms('+1234567890', 'Hello from Twilio!')
# twilio_service.make_call('+1234567890', 'Hello from Twilio!')
