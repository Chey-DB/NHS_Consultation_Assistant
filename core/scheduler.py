from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.twilio_handler import send_reminder_message
from utils.database import database
from datetime import datetime, timedelta
from loguru import logger

async def send_upcoming_appointment_reminders():
    """
    Fetch upcoming appointments within the next hour, send reminders, and mark them as sent.
    """
    try:
        # Query to fetch appointments within the next hour where reminders have not been sent
        query = """
            SELECT a.id, a.appointment_time, p.phone_number
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.reminder_sent = FALSE
            AND a.appointment_time <= :time_limit
        """
        time_limit = datetime.now() + timedelta(hours=1)

        # Fetch upcoming appointments
        upcoming_appointments = await database.fetch_all(query=query, values={"time_limit": time_limit})

        if not upcoming_appointments:
            logger.info("No upcoming appointments to send reminders for.")
            return

        # Send reminders and mark them as sent
        for appointment in upcoming_appointments:
            phone_number = appointment["phone_number"]
            appointment_time = appointment["appointment_time"]

            try:
                # Send SMS reminder
                send_reminder_message(phone_number, appointment_time)
                logger.info(f"Sent reminder to {phone_number} for appointment at {appointment_time}.")

                # Mark the reminder as sent in the database
                update_query = "UPDATE appointments SET reminder_sent = TRUE WHERE id = :appointment_id"
                await database.execute(query=update_query, values={"appointment_id": appointment["id"]})

            except Exception as e:
                logger.error(f"Failed to send reminder for appointment {appointment['id']}: {e}")

    except Exception as e:
        logger.error(f"Error in sending appointment reminders: {e}")

def setup_scheduler():
    """
    Setup the AsyncIO scheduler for sending reminders every 10 minutes.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_upcoming_appointment_reminders, "interval", minutes=10)
    scheduler.start()
    logger.info("Scheduler started: Appointment reminders will be sent every 10 minutes.")
