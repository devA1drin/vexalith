"""
FastAPI application entrypoint.

Startup: create tables + seed domains/questions.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import progress, questions, responses, users
from app.ai.provider import hf_runtime_available
from app.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.schemas.schemas import HealthOut
from app.services.question_bank import seed_domains_and_questions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Adaptive critical-thinking practice: scenario questions, fallacy-aware "
        "feedback (xAI Grok / HF / heuristic), and mastery-based next-item selection."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(responses.router, prefix="/api")
app.include_router(progress.router, prefix="/api")


_db_ready = False


def init_db() -> None:
    """Create tables and seed domains/questions (idempotent).

    Runs at import time so it also works on serverless platforms (Vercel)
    where ASGI lifespan/startup events may not fire, and again lazily on the
    first request if the import-time attempt failed (e.g. a cold-start race).
    """
    global _db_ready
    if _db_ready:
        return
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_domains_and_questions(db)
        logger.info("Database ready; domains & seed questions ensured.")
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
async def ensure_db(request, call_next):
    if not _db_ready:
        try:
            init_db()
        except Exception:
            logger.exception("init_db retry failed")
    return await call_next(request)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    # Clear cached provider so health reflects current env.
    from app.ai.provider import get_ai_provider

    get_ai_provider.cache_clear()
    provider = get_ai_provider()
    db_kind = "sqlite" if settings.database_url.startswith("sqlite") else "postgres"
    return HealthOut(
        status="ok",
        llm_configured=settings.llm_configured,
        hf_available=hf_runtime_available(),
        database=db_kind,
        details={
            "provider": provider.name,
            "llm_model": settings.llm_model if settings.llm_configured else None,
            "llm_base_url": settings.llm_base_url if settings.llm_configured else None,
        },
    )


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
    }
