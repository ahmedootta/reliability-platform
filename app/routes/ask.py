from fastapi import APIRouter

router = APIRouter(prefix="/ask", tags=["ask"])

@router.post("")
def ask():
    ...

@router.get("/{job_id}")
def get_job(job_id: int):
    ...    