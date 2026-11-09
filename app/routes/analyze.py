from fastapi import APIRouter, Depends

from app.ai_client import AIClient, get_ai_client
from app.errors import error_responses
from app.jobs import JOBS, build_analyze_message
from app.schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter(tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses=error_responses(400, 422, 429, 502, 504),  # the failures, shown in Swagger
    summary="Analyse a text in depth with the heavy model",
)
async def analyze(
    body: AnalyzeRequest,
    client: AIClient = Depends(get_ai_client),
):
    message = build_analyze_message(body.text, body.question)
    result = await client.run(JOBS["analyze"], message)  # heavy tier: decided by the job
    return AnalyzeResponse(analysis=result.text, **result.info())
