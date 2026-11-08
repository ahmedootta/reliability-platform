from fastapi import APIRouter, Depends

from app.ai_client import AIClient, get_ai_client
from app.jobs import JOBS, build_analyze_message
from app.schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter(tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyse a text in depth with the heavy model",
)
async def analyze(
    body: AnalyzeRequest,
    client: AIClient = Depends(get_ai_client),
):
    message = build_analyze_message(body.text, body.question)
    result = await client.run(JOBS["analyze"], message)  # heavy tier: decided by the job
    return AnalyzeResponse(analysis=result.text, **result.info())
