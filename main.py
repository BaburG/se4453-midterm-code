import logging
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from typing import Annotated

import crud
import models
import database

# Setup logging
logging.basicConfig(level=logging.INFO)


# Context manager for application lifespan (startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB pool and create tables
    logging.info("Application startup: Initializing database...")
    await database.get_db_pool() # Ensure pool is created
    await database.initialize_db()
    yield
    # Shutdown: Close DB pool
    logging.info("Application shutdown: Closing database connections...")
    await database.close_db_pool()

# Create FastAPI app instance with lifespan manager
app = FastAPI(lifespan=lifespan)

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Middleware for logging requests (similar to Go loggingMiddleware)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Received {request.method} request for {request.url.path}")
    response = await call_next(request)
    return response

# --- Routes ---

@app.get("/hello", response_class=HTMLResponse)
async def read_notes(request: Request):
    """Renders the main page with the list of notes."""
    notes_list = await crud.get_notes()
    return templates.TemplateResponse(
        "index.html", {"request": request, "notes": notes_list}
    )

@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_hello():
    """Redirects the root path "/" to "/hello"."""
    return RedirectResponse(url="/hello")

@app.post("/create", response_class=RedirectResponse)
async def create_note_form(
    title: Annotated[str, Form()],
    body: Annotated[str, Form()]
):
    """Handles the form submission to create a new note."""
    note_data = models.NoteCreate(title=title, body=body)
    created_note = await crud.create_note(note_data)
    if created_note:
        logging.info(f"Note created successfully: ID {created_note.id}")
    else:
        logging.error("Failed to create note from form submission.")
        # Optionally: add user feedback mechanism here (e.g., flash message)
    # Redirect back to the homepage regardless of success/failure for simplicity
    # Status code 303 See Other is appropriate for POST-redirect-GET pattern
    return RedirectResponse(url="/", status_code=303)

# --- Run the application (for development) ---
# Use uvicorn to run the app: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    # This block is mainly for informational purposes.
    # Running directly like this is less common for FastAPI apps than using uvicorn command.
    print("To run the application, use the command:")
    print("uvicorn main:app --reload --host 0.0.0.0 --port 8080")
    # uvicorn.run(app, host="0.0.0.0", port=8080) # This line won't reload on changes
