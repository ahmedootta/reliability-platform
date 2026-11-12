from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_unknown_route_returns_custom_404_for_any_method():
    for method in ["get", "post", "delete"]:
        response = getattr(client, method)("/does-not-exist")
        assert response.status_code == 404
        assert response.json()["error"]["type"] == "not_found"


def test_wrong_method_returns_custom_405():
    response = client.post("/health")
    assert response.status_code == 405
    assert response.json()["error"]["type"] == "method_not_allowed"
    assert "allow" in response.headers


def test_swagger_ui_and_openapi_are_served():
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "AI API Server"
    assert {t["name"] for t in schema["tags"]} == {"health", "classify", "analyze"}
    assert "/health" in schema["paths"]


# ---- the catalogue in app/errors.py is the single source of truth ----

def test_every_error_class_is_consistent():
    from app.errors import _all_errors
    for error in _all_errors():
        assert error.type and error.message and error.description
        assert 400 <= error.status <= 599
    types = [e.type for e in _all_errors()]
    assert len(types) == len(set(types)), "two errors share the same type"


def test_handler_status_and_docs_both_come_from_the_class():
    from fastapi.testclient import TestClient as TC
    from app.errors import AIRateLimited, error_responses, register_exception_handlers
    from fastapi import FastAPI

    probe = FastAPI()
    register_exception_handlers(probe)

    @probe.get("/boom")
    def boom():
        raise AIRateLimited()

    response = TC(probe).get("/boom")
    assert response.status_code == AIRateLimited.status == 429
    assert response.json()["error"] == {"type": AIRateLimited.type, "message": AIRateLimited.message}
    assert AIRateLimited.type in error_responses(429)[429]["content"]["application/json"]["examples"]


def test_error_responses_rejects_a_status_nobody_returns():
    import pytest
    from app.errors import error_responses
    with pytest.raises(ValueError):
        error_responses(418)
