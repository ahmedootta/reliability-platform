from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.errors import register_exception_handlers
from app.routes import ask, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts. Building the settings here makes a bad
    # config (e.g. AI_PROVIDER=groq without a key) stop the server immediately.
    get_settings()
    yield
    # Code after `yield` runs once at shutdown (close clients, etc.)


DESCRIPTION = """
A small server that sits between a client and an AI API.

* The **API key stays on the server**; clients never see it.
* The **endpoint decides the model tier**: `/classify` is always `light` (fast, cheap), `/analyze` is always `heavy` (stronger, slower).
* Every failure uses one error shape: `{"error": {"type": "...", "message": "..."}}`.
"""

TAGS = [
    {"name": "health", "description": "Is the server process up?"},
    {"name": "ask", "description": "Send a prompt to the AI and get the answer back."},
]

app = FastAPI(
    title="AI API Server",
    version="0.1.0",
    description=DESCRIPTION,
    openapi_tags=TAGS,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(ask.router)
