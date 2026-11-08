import groq
import httpx
import pytest

from app.ai_client import AIClient
from app.ai_errors import (
    AIAuthError, AIBadRequest, AIRateLimited, AITimeout, AIUpstreamError,
)
from app.config import Settings
from app.jobs import JOBS

REQUEST = httpx.Request("POST", "http://test")


def fake_client() -> AIClient:
    return AIClient(Settings(_env_file=None, ai_provider="fake"))


async def test_fake_success_light_and_heavy():
    client = fake_client()
    light = await client.run(JOBS["classify"], "hello world")
    heavy = await client.run(JOBS["analyze"], "hello world")
    assert (light.tier, light.model) == ("light", "openai/gpt-oss-20b")
    assert (heavy.tier, heavy.model) == ("heavy", "openai/gpt-oss-120b")
    assert light.text == "[fake light] hello world"
    assert light.input_tokens == 2 and light.latency_ms >= 0


@pytest.mark.parametrize("marker,error", [
    ("__fail:timeout__", AITimeout),
    ("__fail:rate_limited__", AIRateLimited),
    ("__fail:auth__", AIAuthError),
    ("__fail:upstream__", AIUpstreamError),
    ("__fail:bad_request__", AIBadRequest),
])
async def test_fake_failures_on_demand(marker, error):
    with pytest.raises(error):
        await fake_client().run(JOBS["classify"], f"hi {marker}")


def groq_client_raising(exc: Exception) -> AIClient:
    client = AIClient(Settings(_env_file=None, ai_provider="groq", ai_api_key="test-key"))

    async def boom(**kwargs):
        raise exc

    client._groq.chat.completions.create = boom
    return client


def status_error(cls, status):
    return cls("x", response=httpx.Response(status, request=REQUEST), body=None)


@pytest.mark.parametrize("exc,expected", [
    (groq.APITimeoutError(request=REQUEST), AITimeout),  # must NOT become upstream_error
    (groq.APIConnectionError(request=REQUEST), AIUpstreamError),
    (status_error(groq.RateLimitError, 429), AIRateLimited),
    (status_error(groq.AuthenticationError, 401), AIAuthError),
    (status_error(groq.BadRequestError, 400), AIBadRequest),
    (status_error(groq.InternalServerError, 500), AIUpstreamError),
])
async def test_groq_exceptions_are_converted(exc, expected):
    client = groq_client_raising(exc)
    with pytest.raises(expected) as caught:
        await client.run(JOBS["analyze"], "text")
    assert type(caught.value) is expected  # exact type, not just a parent
    assert "test-key" not in caught.value.message
