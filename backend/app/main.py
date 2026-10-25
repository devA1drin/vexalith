"""
Vexalith API — FastAPI entrypoint.

Startup (import time, serverless-friendly): migrate schema (version check +
safe reset), create tables, and upsert seed domains/questions.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, daily, exercises, feedback, meta, progress, questions, responses, users
from app.config import get_settings
from app.db.session import SessionLocal, engine
from app.models.models import Question
from app.schemas.schemas import HealthOut
from app.services.question_bank import migrate_schema, seed_domains_and_questions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Vexalith API",
    version="0.2.0",
    description=(
        "Vexalith — Build Logic. Break Limits. Adaptive programming critical-thinking coach: "
        "code tracing, debugging, complexity, edge cases, code review and data structures, "
        "with explainable feedback (xAI Grok or offline rubric grader) and Elo-based mastery."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

for r in (users.router, questions.router, responses.router, progress.router, daily.router, exercises.router, feedback.router, meta.router, admin.router):
    app.include_router(r, prefix="/api")

_db_ready = False


def init_db() -> None:
    """Migrate + seed (idempotent). Runs at import and lazily on first request if needed."""
    global _db_ready
    if _db_ready:
        return
    migrate_schema(engine)
    db = SessionLocal()
    try:
        seed_domains_and_questions(db)
        logger.info("Database ready; programming domains & questions ensured.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    _db_ready = True


try:
    init_db()
except Exception:  # pragma: no cover - retried lazily per request
    logger.exception("init_db at import failed; will retry on first request")


@app.middleware("http")
async def ensure_db_and_no_cache(request: Request, call_next):
    if not _db_ready:
        try:
            init_db()
        except Exception:
            logger.exception("init_db retry failed")
    response = await call_next(request)
    # Personalized/adaptive API responses must never be cached by browsers or CDNs.
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    from app.ai.provider import get_ai_provider

    get_ai_provider.cache_clear()
    provider = get_ai_provider()
    db_kind = "sqlite" if settings.database_url.startswith("sqlite") else "postgres"
    count = None
    try:
        with SessionLocal() as db:
            count = db.query(Question).count()
    except Exception:  # noqa: BLE001
        logger.exception("health: question count failed")
    return HealthOut(
        status="ok",
        llm_configured=settings.llm_configured,
        auth_configured=bool(settings.backend_jwt_secret),
        database=db_kind,
        question_count=count,
        details={"provider": provider.name, "llm_model": settings.llm_model if settings.llm_configured else None},
    )


@app.get("/")
def root() -> dict:
    return {"app": "Vexalith API", "tagline": "Build Logic. Break Limits.", "docs": "/docs", "health": "/api/health"}
