from fastapi import APIRouter, HTTPException
from utils.database import database
from db.models import calls, patients
from db.queries import get_patient_by_phone_query, get_recent_call_query
from core.logic import is_within_five_minutes
from datetime import datetime

call_router = APIRouter()

@call_router.post("/start_call")
async def start_call(phone_number: str):
    """Start a call session for a patient."""
    query = get_patient_by_phone_query(phone_number)
    patient = await database.fetch_one(query)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    call_start = datetime.now()
    call_query = calls.insert().values(patient_id=patient["id"], call_start=call_start)
    call_id = await database.execute(call_query)
    return {"message": "Call started", "call_id": call_id}

@call_router.get("/recent_call")
async def recent_call(phone_number: str):
    """Check if the patient has a call within the last 5 minutes."""
    patient_query = get_patient_by_phone_query(phone_number)
    patient = await database.fetch_one(patient_query)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    recent_call_query = get_recent_call_query(patient["id"])
    last_call = await database.fetch_one(recent_call_query)

    if not last_call:
        raise HTTPException(status_code=404, detail="No recent calls found")

    if is_within_five_minutes(last_call["call_start"]):
        return {"message": "Recent call found", "call_id": last_call["id"]}

    return {"message": "No recent calls within 5 minutes"}
