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
