"""Request and response shapes. FastAPI validates input against these (422 if wrong)
and uses them to generate the Swagger documentation."""

from typing import Literal

from pydantic import BaseModel, Field


class Usage(BaseModel):
    input_tokens: int = Field(description="Tokens in the prompt we sent")
    output_tokens: int = Field(description="Tokens in the answer (includes reasoning tokens)")


class CallInfo(BaseModel):
    """Facts about the AI call, shared by every successful response."""

    tier: Literal["light", "heavy"] = Field(description="Which model tier was used")
    model: str = Field(description="Exact model name that answered")
    usage: Usage
    latency_ms: int = Field(description="Time spent waiting for the AI provider")


class ClassifyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000, examples=["The delivery was late and the box was damaged."])
    labels: list[str] = Field(
        min_length=2, max_length=20, examples=[["positive", "negative", "neutral"]],
        description="Allowed labels. The answer is always one of these.",
    )


class ClassifyResponse(CallInfo):
    label: str = Field(examples=["negative"])


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000, examples=["Our API p95 latency doubled after the last release..."])
    question: str | None = Field(default=None, max_length=500, examples=["What is the most likely cause?"])


class AnalyzeResponse(CallInfo):
    analysis: str


class ErrorBody(BaseModel):
    type: str = Field(examples=["rate_limited"])
    message: str = Field(examples=["The AI provider is limiting requests. Try again later."])


class ErrorResponse(BaseModel):
    error: ErrorBody
