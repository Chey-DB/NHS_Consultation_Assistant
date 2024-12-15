# File: main.py
# Entry point for the FastAPI application

from fastapi import FastAPI
from api.calls import call_router
from api.reminders import reminder_router
from utils.logger import configure_logger
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure logging
logger = configure_logger()

# Include routers
app.include_router(call_router, prefix="/calls", tags=["Calls"])
app.include_router(reminder_router, prefix="/reminders", tags=["Reminders"])

@app.on_event("startup")
async def startup():
    logger.info("Starting NHS Consultation Assistant...")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down NHS Consultation Assistant...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)