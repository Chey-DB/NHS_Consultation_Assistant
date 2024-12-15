# File: db/queries.py

from sqlalchemy.sql import select
from db.models import patients, calls, responses, appointments

def get_patient_by_phone_query(phone_number: str):
    """
    Fetch a patient by their phone number.
    """
    return select(patients).where(patients.c.phone_number == phone_number)

def get_recent_call_query(patient_id: int):
    """
    Fetch the most recent call for a patient.
    """
    return (
        select(calls)
        .where(calls.c.patient_id == patient_id)
        .order_by(calls.c.call_start.desc())
        .limit(1)
    )

def get_responses_for_call_query(call_id: int):
    """
    Fetch all responses for a specific call.
    """
    return select(responses).where(responses.c.call_id == call_id)

def get_appointments_within_hour_query():
    """
    Fetch appointments scheduled within the next hour.
    """
    from datetime import datetime, timedelta

    now = datetime.now()
    one_hour_later = now + timedelta(hours=1)
    return (
        select(appointments)
        .where(appointments.c.appointment_time <= one_hour_later)
        .where(appointments.c.reminder_sent == False)
    )
