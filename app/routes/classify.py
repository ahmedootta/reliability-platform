from fastapi import APIRouter

router = APIRouter(tags=["classify"])

@router.post("/classify", summary="Classify Ask with Light model")
def classify():
    ...