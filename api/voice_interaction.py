from fastapi import APIRouter, Request
from twilio.twiml.voice_response import VoiceResponse
import os

voice_router = APIRouter()

@voice_router.post("/twilio/voice")
async def handle_voice_call(request: Request):
    """
    Handle incoming voice calls from Twilio.
    """
    response = VoiceResponse()

    # AssemblyAI streaming endpoint
    assembly_stream_url = f"{os.getenv('BASE_URL')}/stream/audio"

    # Forward call audio to AssemblyAI
    response.start_stream(url=assembly_stream_url)

    return response.to_xml()
