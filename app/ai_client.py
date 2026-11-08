"""The ONLY file that talks to the AI provider.

- one client, created once at startup and reused (it holds the key, connection pool,
  timeout, and retry settings)
- model, prompt, and limits are passed per call (they come from the Job)
- every provider failure is converted into one of our AIError types
"""

import logging
import time
from dataclasses import dataclass

import groq
from fastapi import Request

from app.ai_errors import (
    AIAuthError,
    AIBadRequest,
    AIError,
    AIRateLimited,
    AITimeout,
    AIUpstreamError,
)
from app.config import Settings
from app.jobs import Job, model_for

logger = logging.getLogger("ai_client")


@dataclass
class AIResult:
    text: str
    tier: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int

    def info(self) -> dict:
        """The facts every successful response carries (matches schemas.CallInfo)."""
        return {
            "tier": self.tier,
            "model": self.model,
            "usage": {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens},
            "latency_ms": self.latency_ms,
        }


class AIClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._groq: groq.AsyncGroq | None = None
        if settings.ai_provider == "groq":
            self._groq = groq.AsyncGroq(
                api_key=settings.ai_api_key.get_secret_value(),
                timeout=settings.ai_timeout_seconds,
                max_retries=settings.ai_max_retries,
            )

    async def aclose(self) -> None:
        if self._groq is not None:
            await self._groq.close()

    async def run(self, job: Job, user_text: str) -> AIResult:
        model = model_for(job, self.settings)
        started = time.perf_counter()  # measure only the provider call
        try:
            if self._groq is None:
                text, tokens_in, tokens_out = self._fake(job, user_text)
            else:
                text, tokens_in, tokens_out = await self._call_groq(job, model, user_text)
        except AIError as error:
            self._log(job, model, error.type, started)
            raise
        self._log(job, model, "success", started)
        return AIResult(
            text=text,
            tier=job.tier,
            model=model,
            input_tokens=tokens_in,
            output_tokens=tokens_out,
            latency_ms=round((time.perf_counter() - started) * 1000),
        )

    # ---- real provider ----

    async def _call_groq(self, job: Job, model: str, user_text: str) -> tuple[str, int, int]:
        try:
            response = await self._groq.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": job.system_prompt},
                    {"role": "user", "content": user_text},
                ],
                temperature=job.temperature,
                max_completion_tokens=job.max_tokens,
                reasoning_effort=job.reasoning_effort,
                stream=False,
            )
        # ORDER MATTERS: APITimeoutError is a subclass of APIConnectionError, and the
        # specific status errors are subclasses of APIStatusError. Most specific first.
        except groq.APITimeoutError as e:
            raise AITimeout() from e
        except groq.RateLimitError as e:
            raise AIRateLimited() from e
        except (groq.AuthenticationError, groq.PermissionDeniedError) as e:
            raise AIAuthError() from e
        except (groq.BadRequestError, groq.UnprocessableEntityError) as e:
            raise AIBadRequest() from e
        except (groq.APIConnectionError, groq.APIStatusError) as e:
            raise AIUpstreamError() from e
        usage = response.usage
        text = response.choices[0].message.content or ""
        return text, getattr(usage, "prompt_tokens", 0), getattr(usage, "completion_tokens", 0)

    # ---- fake provider (no key, no network) ----

    def _fake(self, job: Job, user_text: str) -> tuple[str, int, int]:
        """Canned answer. A marker in the text triggers a failure on purpose, so tests
        and the Part 3 traffic script can produce every error type on demand."""
        failures = {
            "__fail:timeout__": AITimeout,
            "__fail:rate_limited__": AIRateLimited,
            "__fail:auth__": AIAuthError,
            "__fail:upstream__": AIUpstreamError,
            "__fail:bad_request__": AIBadRequest,
        }
        for marker, error in failures.items():
            if marker in user_text:
                raise error()
        text = f"[fake {job.tier}] {user_text}"
        return text, len(user_text.split()), len(text.split())

    def _log(self, job: Job, model: str, outcome: str, started: float) -> None:
        # Never log the prompt or the key: only facts about the call.
        logger.info(
            "ai call job=%s tier=%s model=%s outcome=%s latency_ms=%d",
            job.name, job.tier, model, outcome, round((time.perf_counter() - started) * 1000),
        )


def get_ai_client(request: Request) -> AIClient:
    """FastAPI dependency: the one client created in `lifespan`."""
    return request.app.state.ai_client
