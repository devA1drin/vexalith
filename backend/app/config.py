"""Application settings loaded from environment variables."""

import os
from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Normalize DB URLs for SQLAlchemy + psycopg (v3).

    - postgres:// / postgresql:// -> postgresql+psycopg://  (Neon/Heroku style URLs)
    - On Vercel (read-only FS except /tmp) a relative SQLite path is moved to /tmp.
    """
    url = (url or "").strip()
    if not url:
        url = "sqlite:///./critical_thinking.db"
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    elif url.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + url[len("postgresql+psycopg2://"):]
    if url.startswith("sqlite:///./") and os.environ.get("VERCEL"):
        url = "sqlite:////tmp/" + url[len("sqlite:///./"):]
    return url


class Settings(BaseSettings):
    """Runtime configuration. Override via env or .env file.

    LLM defaults target xAI's OpenAI-compatible Chat Completions API
    (https://docs.x.ai). Set XAI_API_KEY (preferred) or LLM_API_KEY.
    Without a key the app uses the offline rubric-based heuristic grader.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Vexalith API"
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://frontend:3000"
    # Optional regex for extra allowed origins (e.g. Vercel preview URLs).
    cors_origin_regex: str = ""

    # Database — defaults to SQLite for zero-config local demos.
    # Set DATABASE_URL=postgresql://user:pass@localhost:5432/critical_thinking for Postgres.
    database_url: str = "sqlite:///./critical_thinking.db"

    # xAI Grok (OpenAI-compatible). Docs: https://docs.x.ai
    # Chat Completions: POST {LLM_BASE_URL}/chat/completions
    # Structured JSON: response_format={"type":"json_object"} or json_schema.
    llm_base_url: str = "https://api.x.ai/v1"
    llm_api_key: str = ""  # also populated from XAI_API_KEY via validator
    xai_api_key: str = ""  # preferred env name for xAI
    llm_model: str = "grok-4.7"  # flagship; see https://docs.x.ai/docs/models

    # Shared secret for HS256 JWTs minted by the Next.js server (Auth.js session).
    backend_jwt_secret: str = ""
    # Optional admin maintenance token (sensitive). Admin routes are disabled when unset.
    admin_token: str = ""
    # Who may open the admin dashboard: comma-separated sign-in identities, "provider:account_id"
    # (e.g. "github:1234567"). Not secret. Nobody is an admin while it is empty.
    admin_identities: str = ""

    # Product feedback spam protection
    feedback_max_per_hour: int = 5
    feedback_max_per_day: int = 20

    # Adaptive engine
    initial_mastery: float = 0.5
    mastery_k: float = 0.15  # Elo-style update rate
    target_difficulty_offset: float = 0.05  # prefer slightly harder than mastery

    @model_validator(mode="after")
    def _resolve_api_key(self) -> "Settings":
        """Prefer XAI_API_KEY when LLM_API_KEY is empty."""
        if not self.llm_api_key and self.xai_api_key:
            self.llm_api_key = self.xai_api_key
        self.database_url = normalize_database_url(self.database_url)
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_identity_set(self) -> set[str]:
        return {p.strip().lower() for p in self.admin_identities.split(",") if p.strip()}

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_base_url and self.llm_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
