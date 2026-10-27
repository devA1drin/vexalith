"""
Programming question bank bootstrap + schema versioning.

The seed content lives in ``app/content``. ``init_database`` is idempotent:
- If the stored schema version differs from SCHEMA_VERSION (e.g. the old
  critical-thinking MVP schema), all app tables are dropped and recreated.
  This is acceptable for the MVP (test data only) and documented in README.
- Domains are upserted by slug and questions by (title, language).
"""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.content.bank import SEED_QUESTIONS
from app.content.domains import DOMAINS
from app.db.base import Base
from app.models.models import AppMeta, Difficulty, Question, SkillDomain

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "2-programming-auth"

# Tables from every schema version (dropped on version mismatch).
_ALL_TABLES = [
    "exercise_attempts",
    "daily_completions",
    "hint_usages",
    "user_feedback",
    "question_skips",
    "feedback",
    "responses",
    "skill_masteries",
    "questions",
    "skill_domains",
    "users",
    "app_meta",
]


def _stored_version(engine: Engine) -> str | None:
    insp = inspect(engine)
    if not insp.has_table("app_meta"):
        return None
    with engine.connect() as conn:
        row = conn.execute(text("SELECT value FROM app_meta WHERE key = 'schema_version'")).first()
    return row[0] if row else None


def _drop_everything(engine: Engine) -> None:
    is_pg = engine.dialect.name == "postgresql"
    with engine.begin() as conn:
        for t in _ALL_TABLES:
            conn.execute(text(f'DROP TABLE IF EXISTS "{t}"' + (" CASCADE" if is_pg else "")))
        if is_pg:
            conn.execute(text("DROP TYPE IF EXISTS difficulty_enum"))


def migrate_schema(engine: Engine) -> bool:
    """Ensure the schema matches SCHEMA_VERSION. Returns True if a reset happened."""
    is_pg = engine.dialect.name == "postgresql"
    lock_conn = engine.connect() if is_pg else None
    try:
        if lock_conn is not None:
            # Serialize concurrent cold starts.
            lock_conn.execute(text("SELECT pg_advisory_lock(424242)"))
        version = _stored_version(engine)
        reset = False
        if version != SCHEMA_VERSION:
            insp = inspect(engine)
            if insp.get_table_names():
                logger.warning("Schema version %r != %r: resetting app tables", version, SCHEMA_VERSION)
                _drop_everything(engine)
                reset = True
        Base.metadata.create_all(bind=engine)
        with Session(engine) as db:
            meta = db.get(AppMeta, "schema_version")
            if meta is None:
                db.add(AppMeta(key="schema_version", value=SCHEMA_VERSION))
            else:
                meta.value = SCHEMA_VERSION
            db.commit()
        return reset
    finally:
        if lock_conn is not None:
            lock_conn.execute(text("SELECT pg_advisory_unlock(424242)"))
            lock_conn.close()


def seed_domains_and_questions(db: Session) -> None:
    """Idempotently upsert skill domains and seed questions."""
    slug_to_domain: dict[str, SkillDomain] = {}
    for d in DOMAINS:
        existing = db.query(SkillDomain).filter_by(slug=d["slug"]).one_or_none()
        if existing:
            existing.name = d["name"]
            existing.description = d["description"]
            slug_to_domain[d["slug"]] = existing
        else:
            domain = SkillDomain(**d)
            db.add(domain)
            db.flush()
            slug_to_domain[d["slug"]] = domain

    existing_q = {(q.title, q.language): q for q in db.query(Question).filter_by(source="seed").all()}
    for item in SEED_QUESTIONS:
        key = (item["title"], item["language"])
        q = existing_q.get(key)
        if q is None:
            db.add(
                Question(
                    domain_id=slug_to_domain[item["domain"]].id,
                    difficulty=Difficulty(item["difficulty"]),
                    language=item["language"],
                    title=item["title"],
                    code=item["code"],
                    prompt=item["prompt"],
                    rubric=item["rubric"],
                    source="seed",
                )
            )
        else:  # keep content in sync with the code
            q.domain_id = slug_to_domain[item["domain"]].id
            q.difficulty = Difficulty(item["difficulty"])
            q.code = item["code"]
            q.prompt = item["prompt"]
            q.rubric = item["rubric"]
    db.commit()
    from app.services.question_edits import apply_all

    apply_all(db)  # admin edits outlive the reseed
