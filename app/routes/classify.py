from fastapi import APIRouter, Depends

from app.ai_client import AIClient, get_ai_client
from app.jobs import JOBS, build_classify_message, pick_label
from app.schemas import ClassifyRequest, ClassifyResponse

router = APIRouter(tags=["classify"])


@router.post(
    "/classify",
    response_model=ClassifyResponse,  # the shape of the answer: validated, and shown in Swagger
    summary="Classify a text with the light model",
)
async def classify(
    body: ClassifyRequest,  # 1. FastAPI validates the JSON body here (422 if invalid)
    client: AIClient = Depends(get_ai_client),  # 2. the one shared AI client from lifespan
):
    message = build_classify_message(body.text, body.labels)  # 3. job-specific question
    result = await client.run(JOBS["classify"], message)  # 4. light tier: decided by the job
    label = pick_label(result.text, body.labels)  # 5. the answer must be an allowed label
    return ClassifyResponse(label=label, **result.info())  # 6. build the response
