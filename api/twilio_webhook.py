from fastapi import APIRouter, Request
from fastapi.responses import Response
from services.assembly_ai_handler import stream_audio_to_assembly_ai
from services.eleven_labs_handler import synthesize_speech
from services.grok_handler import process_response
from services.assistant_logic import finalize_call, handle_call_response
from utils.database import database
from db.models import calls
from datetime import datetime
from loguru import logger
from twilio.rest import Client
import os

# Twilio Webhook Router
twilio_webhook_router = APIRouter()

# Load Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@twilio_webhook_router.post("/calls")
async def handle_incoming_call(request: Request):
    """
    Webhook to handle incoming calls from Twilio.
    Steps:
    1. Check if there's a recent call for the same patient.
    2. If no recent call, start a new call session.
    3. Transcribe speech with AssemblyAI, process with Grok, and respond with ElevenLabs.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    caller_number = form_data.get("From")
    logger.info(f"Incoming call from: {caller_number}, Call SID: {call_sid}")

    # Step 1: Check for recent calls (within 5 minutes)
    call_start_time = datetime.now()
    query = calls.select().where(calls.c.call_sid == call_sid)
    existing_call = await database.fetch_one(query)

    if existing_call:
        logger.info(f"Resuming existing call: {existing_call['id']}")
        call_id = existing_call['id']
    else:
        # Start a new call
        call_id = await database.execute(
            calls.insert().values(
                call_sid=call_sid,
                call_start=call_start_time,
                patient_id=None,  # Replace with lookup logic if patient data exists
            )
        )
        logger.info(f"Started new call session with ID: {call_id}")

    try:
        # Step 2: Start transcription workflow
        logger.info(f"Starting transcription for call: {call_id}")
        transcription_text = await stream_audio_to_assembly_ai(call_sid, twilio_client)

        # Step 3: Process transcription with Grok
        _, grok_response = await process_response(transcription_text)
        logger.info(f"Grok response: {grok_response}")

        # Step 4: Generate speech with ElevenLabs
        audio_url = synthesize_speech(grok_response)
        logger.info(f"Audio generated at: {audio_url}")

        # Twilio XML Response to play the generated audio
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Play>{audio_url}</Play>
        </Response>"""

        # Step 5: Save call response to database and finalize
        await handle_call_response(call_id, transcription_text)
        await finalize_call(call_id)

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error during call handling: {e}")
        return Response(
            content="""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say>Sorry, an error occurred while processing your request.</Say>
            </Response>""",
            media_type="application/xml",
        )
