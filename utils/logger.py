from loguru import logger
import sys

def configure_logger():
    """Configure the logger for the application."""
    logger.remove()  # Remove default handler
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
    logger.add("logs/app.log", rotation="1 MB", retention="7 days", level="INFO")
    return logger