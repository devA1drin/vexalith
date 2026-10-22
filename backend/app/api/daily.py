"""Daily challenge: one question per Asia/Manila day, the same for everyone."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import DailyDay, DailyMeOut, DailyOut
from app.services import daily
from app.services.learning import _diff, _question_out

router = APIRouter(prefix="/daily", tags=["daily"])
HISTORY_DAYS = 14


def _summary(db: Session) -> tuple[daily.DailyPick, dict]:
    try:
        pick = daily.pick_for(db, daily.manila_today())
    except LookupError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    q = pick.question
    return pick, {
        "date": pick.day.isoformat(),
        "resets_at": daily.next_reset(),
        "question_id": q.id,
        "title": q.title,
        "language": q.language,
        "domain_slug": pick.domain.slug,
        "domain_name": pick.domain.name,
        "difficulty": _diff(q),
        "kind": (q.rubric or {}).get("kind") or "explain",
    }


@router.get("", response_model=DailyOut)
def today(db: Session = Depends(get_db)) -> DailyOut:
    """Today's challenge (public, no sign-in needed)."""
    return DailyOut(**_summary(db)[1])


@router.get("/me", response_model=DailyMeOut)
def today_for_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DailyMeOut:
    """Today's challenge with your completion status and streaks."""
    pick, summary = _summary(db)
    done = daily.user_days(db, user)
    current, best = daily.streaks(set(done), pick.day)
    last = [pick.day - timedelta(days=i) for i in range(HISTORY_DAYS - 1, -1, -1)]
    return DailyMeOut(
        **summary,
        question=_question_out(pick.question, pick.domain),
        completed=pick.day in done,
        score=done.get(pick.day),
        current_streak=current,
        best_streak=best,
        total_completed=len(done),
        last_days=[DailyDay(date=d.isoformat(), done=d in done, score=done.get(d)) for d in last],
    )
