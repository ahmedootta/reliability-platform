import pytest
from pydantic import ValidationError

from app.config import ENV_FILE, Settings


def make(monkeypatch, **env):
    for key in ["AI_PROVIDER", "AI_API_KEY", "AI_MODEL_LIGHT", "AI_MODEL_HEAVY", "AI_TIMEOUT_SECONDS"]:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return Settings(_env_file=None)  # ignore the real .env so tests are predictable


def test_defaults_to_fake_without_key(monkeypatch):
    s = make(monkeypatch)
    assert s.ai_provider == "fake"
    assert s.ai_model_light == "openai/gpt-oss-20b"


def test_groq_without_key_refuses_to_start(monkeypatch):
    with pytest.raises(ValidationError):
        make(monkeypatch, AI_PROVIDER="groq")


def test_groq_with_key_works_and_key_is_hidden(monkeypatch):
    s = make(monkeypatch, AI_PROVIDER="groq", AI_API_KEY="secret-123")
    assert s.ai_api_key.get_secret_value() == "secret-123"
    assert "secret-123" not in repr(s)


def test_unknown_provider_is_rejected(monkeypatch):
    with pytest.raises(ValidationError):
        make(monkeypatch, AI_PROVIDER="openai")


def test_timeout_is_parsed_as_number(monkeypatch):
    assert make(monkeypatch, AI_TIMEOUT_SECONDS="12.5").ai_timeout_seconds == 12.5


def test_env_file_path_does_not_depend_on_current_folder(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # pretend the server was started from another folder
    assert ENV_FILE.is_absolute()
    assert ENV_FILE.name == ".env"
    assert (ENV_FILE.parent / "app" / "config.py").exists()  # points at the project root


def test_server_startup_fails_on_bad_config(monkeypatch):
    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import app

    get_settings.cache_clear()
    monkeypatch.setenv("AI_PROVIDER", "groq")
    monkeypatch.setenv("AI_API_KEY", "")
    with pytest.raises(ValidationError):
        with TestClient(app):  # entering the context runs the startup (lifespan) code
            pass
    get_settings.cache_clear()
