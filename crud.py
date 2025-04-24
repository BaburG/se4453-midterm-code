import logging
from typing import List, Optional
import database
import models

async def get_notes() -> List[models.Note]:
    """Retrieves all notes from the database, ordered by creation date descending."""
    pool = await database.get_db_pool()
    if not pool:
        logging.error("Cannot get notes: Database pool not available.")
        return []

    async with pool.acquire() as connection:
        try:
            query = "SELECT id, title, body, created_at FROM notes ORDER BY created_at DESC"
            records = await connection.fetch(query)
            # Convert asyncpg records to Pydantic models
            notes_list = [models.Note.parse_obj(dict(record)) for record in records]
            return notes_list
        except Exception as e:
            logging.error(f"Error fetching notes: {e}")
            return []

async def create_note(note: models.NoteCreate) -> Optional[models.Note]:
    """Inserts a new note into the database."""
    pool = await database.get_db_pool()
    if not pool:
        logging.error("Cannot create note: Database pool not available.")
        return None

    async with pool.acquire() as connection:
        try:
            query = """
            INSERT INTO notes (title, body)
            VALUES ($1, $2)
            RETURNING id, title, body, created_at
            """
            record = await connection.fetchrow(query, note.title, note.body)
            if record:
                # Convert the returned record to a Pydantic model
                return models.Note.parse_obj(dict(record))
            else:
                logging.error("Failed to insert note or retrieve the inserted record.")
                return None
        except Exception as e:
            logging.error(f"Error inserting new note: {e}")
            return None 