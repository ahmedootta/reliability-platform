from fastapi import APIRouter

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("")
def ask():
    ...
