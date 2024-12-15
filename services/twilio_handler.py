# File: services/twilio_handler.py

from twilio.rest import Client
import os
from loguru import logger

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize the Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_reminder_message(phone_number: str, appointment_time: str):
    """
    Send an SMS reminder for an appointment.

    Args:
        phone_number (str): The patient's phone number.
        appointment_time (str): The appointment time to include in the message.
    """
    try:
        message_body = f"Reminder: You have an appointment scheduled for {appointment_time}. Please confirm your attendance."
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f"Sent reminder to {phone_number}: {message_body}")
        return message.sid
    except Exception as e:
        logger.error(f"Failed to send reminder to {phone_number}: {e}")
        raise

def make_outgoing_call(phone_number: str, twiml_url: str):
    """
    Initiate an outgoing call to a patient.

    Args:
        phone_number (str): The patient's phone number.
        twiml_url (str): A URL that provides TwiML instructions for the call.
    """
    try:
        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url
        )
        logger.info(f"Outgoing call initiated to {phone_number}")
        return call.sid
    except Exception as e:
        logger.error(f"Failed to make call to {phone_number}: {e}")
        raise
