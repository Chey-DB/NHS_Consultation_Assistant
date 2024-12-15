import requests
import os
from loguru import logger

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

def synthesize_speech(text: str) -> str:
    """
    Convert text into speech using ElevenLabs API and return audio URL.
    """
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {"Authorization": f"Bearer {ELEVEN_LABS_API_KEY}"}
    payload = {"text": text, "voice": "default"}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        audio_url = response.json().get("audio_url")
        logger.info(f"Generated audio URL: {audio_url}")
        return audio_url

    logger.error(f"Failed to synthesize speech: {response.text}")
    raise Exception("Failed to generate speech with ElevenLabs")
