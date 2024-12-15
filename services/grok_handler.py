import openai
import os
from loguru import logger

# Load Grok API key from environment variables
GROK_API_KEY = os.getenv("GROK_API_KEY")

# Configure the Grok API
openai.api_key = GROK_API_KEY
openai.api_base = "https://api.x.ai/v1"  # Grok API base

# System prompt to guide the assistant's behavior
SYSTEM_PROMPT = """
You are an NHS Consultation Assistant designed to interact with patients over the phone.
Your goal is to ask a series of structured questions needed to fill out a GP consultation form on the patient's behalf.
Ensure clarity, politeness, and provide one question at a time. 

The required questions are:
1. What is your full name?
2. What is your date of birth?
3. What is your phone number?
4. What is your reason for booking this appointment?
5. Have you experienced these symptoms before?
6. How long have you had these symptoms?
7. Are you currently taking any medication? If yes, please list them.
8. Do you have any known allergies?
9. Is there anything else you would like the doctor to know?

You must wait for the patient to answer each question before moving on.
Once all questions are answered, summarize their responses in the following JSON format:

{
    "full_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "phone_number": "string",
    "reason_for_appointment": "string",
    "experienced_before": "yes/no",
    "duration_of_symptoms": "string",
    "current_medication": "string",
    "known_allergies": "string",
    "additional_notes": "string"
}

If the patient provides partial information, ask follow-up questions to clarify. 
Be patient, and ensure all data is complete before concluding.
"""

# Define the Grok model to be used
MODEL = "grok-2"

def process_response(patient_input: str, conversation_history: list) -> tuple:
    """
    Process the patient's response through Grok to generate the next question or action.

    Args:
        patient_input (str): The latest input from the patient.
        conversation_history (list): A history of previous interactions.

    Returns:
        tuple: A question or final response, and the updated conversation history.
    """
    try:
        # Append the patient's input to conversation history
        conversation_history.append({"role": "user", "content": patient_input})

        # Prepare the full message for Grok
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

        # Call Grok API
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        # Extract assistant's reply
        assistant_reply = response["choices"][0]["message"]["content"]

        # Append the assistant's reply to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_reply})

        logger.info(f"Grok Response: {assistant_reply}")
        return assistant_reply, conversation_history

    except Exception as e:
        logger.error(f"Error processing Grok response: {e}")
        raise

def extract_patient_data(final_response: str) -> dict:
    """
    Extract structured patient data from Grok's final JSON response.

    Args:
        final_response (str): The assistant's final summary in JSON format.

    Returns:
        dict: Parsed patient data.
    """
    import json
    try:
        data = json.loads(final_response)
        logger.info("Extracted patient data successfully.")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Grok's response: {e}")
        raise ValueError("Invalid JSON format received from Grok.")
