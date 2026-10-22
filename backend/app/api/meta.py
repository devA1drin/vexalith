"""Public metadata: domains, languages and question-bank counts (no question content)."""

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.content.domains import DOMAINS, LANGUAGES
from app.db.session import get_db
from app.models.models import Question

router = APIRouter(tags=["meta"])


@router.get("/languages")
def languages() -> list[dict]:
    return LANGUAGES


@router.get("/domains")
def domains() -> list[dict]:
    return DOMAINS


@router.get("/catalog")
def catalog(db: Session = Depends(get_db)) -> dict:
    """How many questions the live database serves, per language and per question kind."""
    rows = db.query(Question.language, Question.rubric).all()
    by_lang = Counter(lang for lang, _ in rows)
    by_kind = Counter(((rubric or {}).get("kind") or "explain") for _, rubric in rows)
    return {
        "total": len(rows),
        "languages": {lang["slug"]: by_lang.get(lang["slug"], 0) for lang in LANGUAGES},
        "kinds": dict(sorted(by_kind.items())),
    }
