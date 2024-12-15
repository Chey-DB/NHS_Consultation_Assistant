import websockets
import json
import os
from services.grok_handler import process_response
from services.eleven_labs_handler import synthesize_speech
from twilio.rest import Client
from loguru import logger

ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

async def stream_audio_to_assembly_ai(call_sid: str, twilio_client: Client):
    """
    Stream live audio to AssemblyAI and process real-time transcriptions.
    """
    url = "wss://api.assemblyai.com/v2/realtime/ws"
    headers = {"Authorization": ASSEMBLY_AI_API_KEY}

    async with websockets.connect(url, extra_headers=headers) as websocket:
        logger.info("Connected to AssemblyAI for real-time transcription.")

        try:
            # Listen to AssemblyAI's responses
            async for message in websocket:
                data = json.loads(message)

                if "text" in data:
                    logger.info(f"Transcription: {data['text']}")

                    # Process transcription through Grok
                    _, grok_response = process_response(data["text"])

                    # Generate speech response with ElevenLabs
                    audio_url = synthesize_speech(grok_response)

                    # Twilio plays the response
                    twilio_client.calls(call_sid).update(twiml=f'<Response><Play>{audio_url}</Play></Response>')

        except Exception as e:
            logger.error(f"Error in AssemblyAI streaming: {e}")
