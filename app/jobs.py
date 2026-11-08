"""What each job is: its tier, prompt, and limits, plus job-specific input and output handling.

The endpoint only names the job (`JOBS["classify"]`). Everything about HOW the AI is
called for that job lives here, so routes stay thin and this file is easy to test
(no HTTP, no Groq).
"""

from dataclasses import dataclass
from typing import Literal

from app.ai_errors import AIBadOutput
from app.config import Settings

Tier = Literal["light", "heavy"]


@dataclass(frozen=True)
class Job:
    name: str
    tier: Tier
    system_prompt: str
    max_tokens: int
    temperature: float
    reasoning_effort: Literal["low", "medium", "high"]


JOBS: dict[str, Job] = {
    "classify": Job(
        name="classify",
        tier="light",  # cheap and fast: a short answer is enough
        system_prompt=(
            "You are a text classifier. Reply with exactly one of the allowed labels "
            "and nothing else: no explanation, no punctuation."
        ),
        max_tokens=512,  # reasoning models spend tokens thinking, so not tiny
        temperature=0,
        reasoning_effort="low",
    ),
    "analyze": Job(
        name="analyze",
        tier="heavy",  # stronger and slower: multi-step reasoning, longer answer
        system_prompt=(
            "You are a careful analyst. Read the text and give a clear analysis: "
            "key points, risks or problems, and a short conclusion."
        ),
        max_tokens=2048,
        temperature=0.3,
        reasoning_effort="medium",
    ),
}


def model_for(job: Job, settings: Settings) -> str:
    """tier -> model name, taken from the settings (.env)."""
    return settings.ai_model_light if job.tier == "light" else settings.ai_model_heavy


# ---- classify: building the question and reading the answer ----


def build_classify_message(text: str, labels: list[str]) -> str:
    return f"Allowed labels: {', '.join(labels)}\n\nText:\n{text}"


def pick_label(reply: str, labels: list[str]) -> str:
    """Return the allowed label that appears in the model's reply.

    The model may add spaces, quotes, or different casing, so match loosely. If the
    reply contains none of the labels, we cannot trust it: raise AIBadOutput.
    """
    cleaned = reply.strip().strip("\"'.`").lower()
    for label in labels:  # exact match first
        if cleaned == label.strip().lower():
            return label
    for label in labels:  # then "label appears inside the reply"
        if label.strip().lower() in cleaned:
            return label
    raise AIBadOutput("The AI did not return one of the allowed labels.")


# ---- analyze: building the question ----


def build_analyze_message(text: str, question: str | None) -> str:
    if question:
        return f"Question to focus on: {question}\n\nText:\n{text}"
    return f"Text:\n{text}"
