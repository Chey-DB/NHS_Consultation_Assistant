# File: db/init_db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncConnection
from db.models import metadata
from loguru import logger
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    """
    Initialize the database and create all tables asynchronously.
    """
    try:
        logger.info("Initializing the database...")
        engine = create_async_engine(DATABASE_URL, echo=True)  # Use async engine
        async with engine.begin() as conn:  # Use async connection
            await conn.run_sync(metadata.create_all)  # Run synchronous DDL operations in async mode
        await engine.dispose()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize the database: {e}")
        raise
