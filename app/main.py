from fastapi import FastAPI
from app.routes import ask, health

app = FastAPI(title="AI API Server")

app.include_router(health.router)
app.include_router(ask.router)
