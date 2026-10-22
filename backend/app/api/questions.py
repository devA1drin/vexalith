"""Adaptive next-question and skip endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import Question, User
from app.schemas.schemas import QuestionOut, SkipOut
from app.services.learning import get_next_question, skip_question

router = APIRouter(prefix="/questions", tags=["questions"])

Language = Literal["python", "javascript", "php", "html", "css", "general"]
Focus = Literal["fundamentals"]


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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuestionOut:
    try:
        return get_next_question(db, user, language=language, exclude_ids=_parse_exclude(exclude), focus=focus)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{question_id}/skip", response_model=SkipOut)
def skip(
    question_id: int,
    language: Language = Query("python"),
    focus: Focus | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkipOut:
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    skip_question(db, user=user, question=question)
    nxt = get_next_question(
        db, user, language=language, exclude_ids={question_id}, avoid_domain_ids={question.domain_id},
        focus=focus,
    )
    return SkipOut(skipped_question_id=question_id, next_question=nxt)
