# File: utils/database.py
from databases import Database
from loguru import logger
from db.init_db import init_db  # Import the async init_db function
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize database instance with connection pool limits
database = Database(
    DATABASE_URL,
    min_size=1,  # Minimum number of connections
    max_size=5,  # Maximum number of connections (adjust based on your plan)
)

async def initialize_database():
    """
    Initialize the database connection and call init_db().
    """
    try:
        logger.info("Connecting to the database...")
        await database.connect()
        await init_db()  # Await the async init_db function
        logger.info("Database connection and initialization completed.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_database():
    """
    Close the database connection.
    """
    try:
        await database.disconnect()
        logger.info("Database connection closed.")
    except Exception as e:
        logger.error(f"Failed to close database connection: {e}")
        raise
