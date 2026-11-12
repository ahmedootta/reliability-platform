from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health", summary="Liveness check", description="Returns 200 when the server process is running. It does not call the AI API.")
def health():
    return {"status": "ok"}