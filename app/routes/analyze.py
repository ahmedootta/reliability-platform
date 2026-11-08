from fastapi import APIRouter

router = APIRouter(tags=["analyze"])

@router.post("/analyze", summary="Analayze with heavy model")
def analyze():
    ...