from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ai_client import AIClient
from app.config import get_settings
from app.errors import register_exception_handlers
from app.routes import analyze, classify, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts. Building the settings here makes a bad
    # config (e.g. AI_PROVIDER=groq without a key) stop the server immediately.
    settings = get_settings()
    app.state.ai_client = AIClient(settings)  # one client, reused by every request
    yield
    # Code after `yield` runs once at shutdown
    await app.state.ai_client.aclose()


DESCRIPTION = """
A small server that sits between a client and an AI API.

* The **API key stays on the server**; clients never see it.
* The **endpoint decides the model tier**: `/classify` is always `light` (fast, cheap), `/analyze` is always `heavy` (stronger, slower).
* Every failure uses one error shape: `{"error": {"type": "...", "message": "..."}}`.
"""

TAGS = [
    {"name": "health", "description": "Is the server process up?"},
    {"name": "classify", "description": "Pick one label for a text. Always uses the light model."},
    {"name": "analyze", "description": "Analyse a text in depth. Always uses the heavy model."},
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
app.include_router(classify.router)
app.include_router(analyze.router)
