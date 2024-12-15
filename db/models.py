# File: db/models.py
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey
)
from sqlalchemy.sql import func  # Import func for SQL functions like now()

metadata = MetaData()

# Patients table
patients = Table(
    "patients",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("phone_number", String(15), unique=True, nullable=False),
    Column("name", String(100), nullable=False),
    Column("spelled_out_name", String(255)),
    Column("name_correct_flag", Boolean, default=False),
)

# Calls table
calls = Table(
    "calls",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("patient_id", Integer, ForeignKey("patients.id", ondelete="CASCADE")),
    Column("call_start", TIMESTAMP, nullable=False, default=func.now()),
    Column("call_end", TIMESTAMP),
    Column("call_duration", TIMESTAMP, nullable=True),
)

# Responses table
responses = Table(
    "responses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("patient_id", Integer, ForeignKey("patients.id", ondelete="CASCADE")),
    Column("question", String(255), nullable=False),
    Column("response", Text, nullable=False),
    Column("call_id", Integer, ForeignKey("calls.id", ondelete="CASCADE")),
    Column("created_at", TIMESTAMP, default=func.now()),  # Fixed here
)

# Appointments table
appointments = Table(
    "appointments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("patient_id", Integer, ForeignKey("patients.id", ondelete="CASCADE")),
    Column("appointment_time", TIMESTAMP, nullable=False),
    Column("reminder_sent", Boolean, default=False),
    Column("created_at", TIMESTAMP, default=func.now()),  # Fixed here
    Column("updated_at", TIMESTAMP, default=func.now(), onupdate=func.now()),  # Fixed here
)
