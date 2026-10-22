"""Schema versioning: old MVP schema is reset and reseeded."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.models.models import Question, SkillDomain
from app.services.question_bank import SCHEMA_VERSION, migrate_schema, seed_domains_and_questions


def test_old_schema_is_reset_and_reseeded(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/old.db")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, display_name VARCHAR(128))"))
        conn.execute(text("CREATE TABLE skill_domains (id INTEGER PRIMARY KEY, slug VARCHAR(64), name VARCHAR(128), description TEXT)"))
        conn.execute(text("INSERT INTO skill_domains (slug, name, description) VALUES ('fallacy_detection', 'Fallacy', '')"))
    assert migrate_schema(engine) is True
    cols = {c["name"] for c in inspect(engine).get_columns("users")}
    assert {"auth_provider", "provider_account_id"} <= cols
    with Session(engine) as db:
        seed_domains_and_questions(db)
        seed_domains_and_questions(db)  # idempotent
        slugs = {d.slug for d in db.query(SkillDomain).all()}
        assert "fallacy_detection" not in slugs and "debugging" in slugs
        from app.content.bank import SEED_QUESTIONS
        assert db.query(Question).count() == len(SEED_QUESTIONS)
        v = db.execute(text("SELECT value FROM app_meta WHERE key='schema_version'")).scalar()
        assert v == SCHEMA_VERSION
    assert migrate_schema(engine) is False  # second run: no reset
