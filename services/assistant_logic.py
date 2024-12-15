from services.grok_handler import process_response, extract_patient_data
from services.sheets_handler import save_to_sheet
from utils.database import database  # Only the database instance
from db.models import responses, calls  # Import responses and calls from db.models
from datetime import datetime
from loguru import logger


async def handle_call_response(call_id: int, patient_input: str, conversation_history: list):
    """
    Handles processing a patient's response during a call.

    Args:
        call_id (int): The ID of the call session.
        patient_input (str): The patient's response to the previous question.
        conversation_history (list): The conversation history with Grok.

    Returns:
        dict: Contains the next question or the final summary.
    """
    try:
        # Process the patient's response with Grok
        grok_reply, updated_conversation = process_response(patient_input, conversation_history)

        # Check if Grok has provided a final JSON summary
        if grok_reply.startswith("{") and grok_reply.endswith("}"):
            logger.info("Final summary received from Grok.")
            patient_data = extract_patient_data(grok_reply)

            # Save the final data to the database and Google Sheets
            await save_final_data(call_id, patient_data)

            return {"status": "completed", "data": patient_data}

        # Return the next question
        logger.info(f"Next question from Grok: {grok_reply}")
        return {"status": "ongoing", "next_question": grok_reply, "conversation": updated_conversation}

    except Exception as e:
        logger.error(f"Error handling call response: {e}")
        return {"status": "error", "message": str(e)}


async def save_final_data(call_id: int, patient_data: dict):
    """
    Saves the final patient data to the database and Google Sheets.

    Args:
        call_id (int): The ID of the call session.
        patient_data (dict): The structured patient data.
    """
    try:
        # Save to database
        logger.info("Saving final data to database...")
        await database.execute(
            responses.insert().values(
                call_id=call_id,
                question="Final Summary",
                response=str(patient_data),
                created_at=datetime.now(),
            )
        )

        # Save to Google Sheets
        logger.info("Saving final data to Google Sheets...")
        save_to_sheet(
            call_id=call_id,
            question="Final Summary",
            response=str(patient_data)
        )
        logger.info("Final data saved successfully.")

    except Exception as e:
        logger.error(f"Failed to save final data: {e}")
        raise


async def finalize_call(call_id: int):
    """
    Finalize the call by recording the end time and call duration.

    Args:
        call_id (int): The ID of the call session to finalize.

    Returns:
        dict: Summary of the finalized call.
    """
    try:
        call_end_time = datetime.now()

        # Retrieve the call's start time
        query = calls.select().where(calls.c.id == call_id)
        call_record = await database.fetch_one(query)

        if not call_record:
            raise ValueError(f"Call ID {call_id} not found in the database.")

        call_start_time = call_record["call_start"]
        call_duration = call_end_time - call_start_time

        # Update the database with call end time and duration
        update_query = calls.update().where(calls.c.id == call_id).values(
            call_end=call_end_time,
            call_duration=call_duration
        )
        await database.execute(update_query)

        logger.info(f"Call {call_id} finalized successfully.")

        return {
            "call_id": call_id,
            "call_start": call_start_time,
            "call_end": call_end_time,
            "duration": call_duration
        }

    except Exception as e:
        logger.error(f"Error finalizing call: {e}")
        raise
