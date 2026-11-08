import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture
def client(monkeypatch):
    # A real env var beats .env, so the tests always run in fake mode (no key, no network).
    monkeypatch.setenv("AI_PROVIDER", "fake")
    get_settings.cache_clear()
    with TestClient(app) as c:  # `with` runs lifespan, which creates the AI client
        yield c
    get_settings.cache_clear()


LABELS = ["positive", "negative", "neutral"]


def test_classify_uses_the_light_model(client):
    response = client.post("/classify", json={"text": "Great service!", "labels": LABELS})
    assert response.status_code == 200
    body = response.json()
    assert body["tier"] == "light"
    assert body["model"] == "openai/gpt-oss-20b"
    assert body["label"] in LABELS
    assert set(body["usage"]) == {"input_tokens", "output_tokens"}


def test_analyze_uses_the_heavy_model(client):
    response = client.post("/analyze", json={"text": "Latency doubled.", "question": "Why?"})
    assert response.status_code == 200
    body = response.json()
    assert body["tier"] == "heavy"
    assert body["model"] == "openai/gpt-oss-120b"
    assert body["analysis"].startswith("[fake heavy]")


def test_analyze_question_is_optional(client):
    assert client.post("/analyze", json={"text": "Latency doubled."}).status_code == 200


@pytest.mark.parametrize("payload", [
    {"text": "", "labels": LABELS},                 # empty text
    {"text": "hi", "labels": ["only-one"]},          # fewer than 2 labels
    {"text": "hi"},                                  # labels missing
    {"text": "x" * 4001, "labels": LABELS},          # text too long
])
def test_classify_rejects_invalid_input(client, payload):
    assert client.post("/classify", json=payload).status_code == 422


@pytest.mark.parametrize("payload", [{}, {"text": ""}, {"text": "x" * 8001}])
def test_analyze_rejects_invalid_input(client, payload):
    assert client.post("/analyze", json=payload).status_code == 422


def test_swagger_shows_the_request_and_response_models(client):
    paths = client.get("/openapi.json").json()["paths"]
    classify = paths["/classify"]["post"]
    assert classify["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith("ClassifyRequest")
    assert classify["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith("ClassifyResponse")


# ---- failures: every AI error becomes the right status in our JSON shape ----

@pytest.mark.parametrize("marker, status, error_type", [
    ("__fail:timeout__", 504, "timeout"),
    ("__fail:rate_limited__", 429, "rate_limited"),
    ("__fail:auth__", 502, "auth_error"),
    ("__fail:upstream__", 502, "upstream_error"),
    ("__fail:bad_request__", 400, "bad_request"),
])
def test_ai_failures_map_to_http_errors(client, marker, status, error_type):
    classify = client.post("/classify", json={"text": marker, "labels": LABELS})
    analyze = client.post("/analyze", json={"text": marker})
    for response in (classify, analyze):
        assert response.status_code == status
        error = response.json()["error"]
        assert error["type"] == error_type
        assert marker not in error["message"]  # messages never echo the input


def test_unusable_model_answer_is_a_502(client):
    # The fake model answers "I cannot decide.", which is none of the labels.
    response = client.post("/classify", json={"text": "__fail:bad_output__", "labels": LABELS})
    assert response.status_code == 502
    assert response.json()["error"]["type"] == "bad_output"


def test_invalid_input_uses_our_error_shape(client):
    response = client.post("/classify", json={"text": "", "labels": ["only-one"]})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["type"] == "invalid_input"
    assert {f["field"] for f in error["fields"]} == {"text", "labels"}
