"""Adaptive next-question and skip endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import Question, User
from app.schemas.schemas import HintsOut, QuestionOut, SkipOut
from app.services import hints as hint_service
from app.services.learning import get_next_question, skip_question

router = APIRouter(prefix="/questions", tags=["questions"])

Language = Literal["python", "javascript", "php", "cpp", "html", "css", "general"]
Focus = Literal["fundamentals"]
Difficulty = Literal["adaptive", "beginner", "intermediate", "advanced"]
TOPIC_PATTERN = r"^[a-z_]{2,40}$"


def _parse_exclude(raw: str | None) -> set[int]:
    if not raw:
        return set()
    out: set[int] = set()
    for part in raw.split(",")[:20]:
        part = part.strip()
        if part.isdigit():
            out.add(int(part))
    return out


@router.get("/next", response_model=QuestionOut)
def next_question(
    language: Language = Query("python"),
    exclude: str | None = Query(None, description="Comma-separated question ids to avoid"),
    focus: Focus | None = Query(None, description="Restrict practice to one skill (fundamentals)"),
    difficulty: Difficulty = Query("adaptive", description="adaptive (Elo) or a fixed level"),
    topic: str | None = Query(None, pattern=TOPIC_PATTERN, description="Skill-domain slug"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuestionOut:
    try:
        return get_next_question(
            db, user, language=language, exclude_ids=_parse_exclude(exclude), focus=focus,
            difficulty=difficulty, topic=topic,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{question_id}/skip", response_model=SkipOut)
def skip(
    question_id: int,
    language: Language = Query("python"),
    focus: Focus | None = Query(None),
    difficulty: Difficulty = Query("adaptive"),
    topic: str | None = Query(None, pattern=TOPIC_PATTERN),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkipOut:
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    skip_question(db, user=user, question=question)
    nxt = get_next_question(
        db, user, language=language, exclude_ids={question_id}, avoid_domain_ids={question.domain_id},
        focus=focus, difficulty=difficulty, topic=topic,
    )
    return SkipOut(skipped_question_id=question_id, next_question=nxt)


def _hints_out(db: Session, user: User, question: Question, shown: int | None = None) -> HintsOut:
    all_hints = hint_service.question_hints(question)
    shown = hint_service.revealed_levels(db, user, question) if shown is None else shown
    return HintsOut(
        question_id=question.id,
        revealed=all_hints[:shown],
        hint_count=len(all_hints),
        penalty_per_hint=hint_service.PENALTY_PER_HINT,
        penalty=hint_service.penalty_for(shown),
    )


@router.get("/{question_id}/hints", response_model=HintsOut)
def list_hints(question_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> HintsOut:
    """Hints already revealed for the current attempt."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return _hints_out(db, user, question)


@router.post("/{question_id}/hints", response_model=HintsOut)
def reveal_hint(question_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> HintsOut:
    """Reveal the next hint level (one at a time; each costs 10% of the score, max 30%)."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return _hints_out(db, user, question, hint_service.reveal_next(db, user, question))
