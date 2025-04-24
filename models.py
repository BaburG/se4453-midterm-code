from pydantic import BaseModel
from datetime import datetime

# Pydantic model for creating a new note (input)
class NoteCreate(BaseModel):
    title: str
    body: str

# Pydantic model for reading a note (output/database representation)
class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime

    # ORM Mode allows Pydantic to read data from ORM objects (like asyncpg records)
    class Config:
        orm_mode = True 