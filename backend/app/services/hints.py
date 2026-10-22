"""Progressive hints: reveal one level at a time and price them into the score."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import HintUsage, Question, Response, User

PENALTY_PER_HINT = 0.1  # each revealed hint takes 10% off the answer's score
MAX_PENALTY = 0.3


def question_hints(q: Question) -> list[str]:
    return list((q.rubric or {}).get("hints") or [])


def _since(db: Session, user: User, question: Question) -> datetime | None:
    """Hints count for the current attempt: those revealed after the learner's last answer to it."""
    last = (
        db.query(Response.created_at)
        .filter(Response.user_id == user.id, Response.question_id == question.id)
        .order_by(Response.created_at.desc())
        .first()
    )
    return last[0] if last else None


def revealed_levels(db: Session, user: User, question: Question) -> int:
    q = db.query(HintUsage).filter(HintUsage.user_id == user.id, HintUsage.question_id == question.id)
    since = _since(db, user, question)
    if since is not None:
        q = q.filter(HintUsage.created_at > since)
    return min(q.count(), len(question_hints(question)))


def penalty_for(levels: int) -> float:
    return round(min(MAX_PENALTY, PENALTY_PER_HINT * levels), 4)


def reveal_next(db: Session, user: User, question: Question) -> int:
    """Reveal the next hint level (no-op once all are shown). Returns the number now revealed."""
    hints = question_hints(question)
    shown = revealed_levels(db, user, question)
    if shown < len(hints):
        db.add(HintUsage(user_id=user.id, question_id=question.id, level=shown + 1))
        db.commit()
        shown += 1
    return shown
