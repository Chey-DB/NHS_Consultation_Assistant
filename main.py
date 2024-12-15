# File: main.py
# Entry point for the FastAPI application

from fastapi import FastAPI
from fastapi.routing import APIRouter
from api.calls import call_router
from api.reminders import reminder_router
from api.twilio_webhook import twilio_webhook_router  # Import the Twilio webhook router
from utils.logger import configure_logger
from utils.database import initialize_database, close_database
from dotenv import load_dotenv
import contextlib

load_dotenv()

# Configure logging
logger = configure_logger()

# Define lifespan for app lifecycle events
@contextlib.asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    Lifespan event handler for app lifecycle management.
    """
    logger.info("Starting NHS Consultation Assistant...")
    await initialize_database()
    yield  # The application runs while paused here
    logger.info("Shutting down NHS Consultation Assistant...")
    await close_database()

# Create FastAPI app with lifespan
app = FastAPI(lifespan=app_lifespan)

# Include routers
app.include_router(call_router, prefix="/calls", tags=["Calls"])
app.include_router(reminder_router, prefix="/reminders", tags=["Reminders"])
app.include_router(twilio_webhook_router, prefix="/twilio", tags=["Twilio Webhooks"])  # Add this line

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
