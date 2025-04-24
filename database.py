import asyncpg
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL") # e.g. "postgresql://user:password@host:port/dbname"

if not DATABASE_URL:
    # Fallback to individual components if DATABASE_URL is not set
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "notesdb")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DATABASE_URL = os.getenv("database-url","")
else:
    # Parse DATABASE_URL to potentially extract DB_NAME if needed elsewhere
    # Basic parsing, might need improvement for complex URLs
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(DATABASE_URL)
        DB_NAME = parsed_url.path.lstrip('/')
        if not DB_NAME:
            DB_NAME = os.getenv("DB_NAME", "notesdb") # Fallback if path is empty
    except ImportError:
        DB_NAME = os.getenv("DB_NAME", "notesdb") # Fallback if urllib not available or fails
    except Exception as e:
        logging.warning(f"Could not parse DB_NAME from DATABASE_URL: {e}. Using fallback.")
        DB_NAME = os.getenv("DB_NAME", "notesdb")


pool = None

async def get_db_pool():
    """Creates and returns the database connection pool."""
    global pool
    if pool is None:
        try:
            pool = await asyncpg.create_pool(DATABASE_URL)
            logging.info("Database connection pool created successfully.")
        except Exception as e:
            logging.error(f"Failed to create database connection pool: {e}")
            # Depending on the desired behavior, you might want to raise the exception
            # or handle it in a way that allows the application to start (perhaps with limited functionality)
            raise
    return pool

async def close_db_pool():
    """Closes the database connection pool."""
    global pool
    if pool:
        await pool.close()
        pool = None
        logging.info("Database connection pool closed.")

async def initialize_db():
    """Initializes the database by creating the notes table if it doesn't exist."""
    db_pool = await get_db_pool()
    if not db_pool:
        logging.error("Cannot initialize database: Connection pool is not available.")
        return

    async with db_pool.acquire() as connection:
        try:
            # Check if DB exists (Note: asyncpg connects to a specific DB)
            # We assume the DB exists based on DATABASE_URL. Creating DBs dynamically is complex.

            # Create the "notes" table if it doesn't exist
            query = """
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            await connection.execute(query)
            logging.info("Database table 'notes' initialized successfully (or already exists).")
        except Exception as e:
            logging.error(f"Error initializing database table: {e}")
            # Decide how to handle this error - potentially raise it
            # raise 