from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# <project root>/.env, no matter which folder the server is started from
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Settings read from environment variables and the .env file.

    Field name -> variable name: ai_provider -> AI_PROVIDER (case-insensitive).
    Real environment variables win over values in .env.
    """

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    ai_provider: Literal["fake", "groq"] = "fake"
    ai_api_key: SecretStr = SecretStr("")  # SecretStr hides the value in repr/logs
    ai_model_light: str = "openai/gpt-oss-20b"
    ai_model_heavy: str = "openai/gpt-oss-120b"
    ai_timeout_seconds: float = 30

    @model_validator(mode="after")
    def key_required_for_real_provider(self):
        if self.ai_provider == "groq" and not self.ai_api_key.get_secret_value().strip():
            raise ValueError("AI_API_KEY is required when AI_PROVIDER=groq")
        return self


@lru_cache
def get_settings() -> Settings:
    """Build settings once and reuse them (also a FastAPI dependency)."""
    return Settings()
