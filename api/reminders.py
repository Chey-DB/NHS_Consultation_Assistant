from fastapi import APIRouter
from services.twilio_handler import send_reminder_message
from utils.database import database
from db.models import appointments, patients
from db.queries import get_appointments_within_hour_query
from datetime import datetime

reminder_router = APIRouter()

@reminder_router.get("/send_reminders")
async def send_reminders():
    """
    Send reminders for upcoming appointments within the next hour.
    """
    appointment_query = get_appointments_within_hour_query()
    upcoming_appointments = await database.fetch_all(appointment_query)

    for appointment in upcoming_appointments:
        patient_query = patients.select().where(patients.c.id == appointment["patient_id"])
        patient = await database.fetch_one(patient_query)

        send_reminder_message(patient["phone_number"], appointment["appointment_time"])

        update_query = appointments.update().where(appointments.c.id == appointment["id"]).values(reminder_sent=True)
        await database.execute(update_query)

    return {"message": "Reminders sent successfully"}
