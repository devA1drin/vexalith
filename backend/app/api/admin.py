"""Admin maintenance: purge specific users (and everything they own).

Disabled (404) unless ADMIN_TOKEN (>= 32 chars) is configured. Callers must send it in
the X-Admin-Token header; comparison is constant-time. Users are addressed by their
stable provider identity ("provider:account_id"), never by name.
"""

from __future__ import annotations

import hmac

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.models import Bookmark, DailyCompletion, ExerciseAttempt, ExerciseHelp, Feedback, HintUsage, LearnerProfile, PathActivity, PathSkip, QuestionSkip, QuizAnswer, QuizSession, Response, ReviewRetry, SkillMastery, User, UserBadge, UserFeedback, UserSettings, XpEvent

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = get_settings().admin_token
    if not expected or len(expected) < 32:
        raise HTTPException(status_code=404, detail="Not Found")
    if not x_admin_token or not hmac.compare_digest(x_admin_token.encode(), expected.encode()):
        raise HTTPException(status_code=403, detail="Forbidden")


class PurgeRequest(BaseModel):
    identities: list[str] = Field(min_length=1, max_length=20)
    dry_run: bool = True


@router.post("/purge-users", dependencies=[Depends(require_admin)])
def purge_users(body: PurgeRequest, db: Session = Depends(get_db)) -> dict:
    report: list[dict] = []
    for ident in body.identities:
        provider, _, pid = ident.partition(":")
        user = db.scalar(select(User).where(User.auth_provider == provider, User.provider_account_id == pid))
        if not user:
            report.append({"identity": ident, "found": False})
            continue
        resp_ids = list(db.scalars(select(Response.id).where(Response.user_id == user.id)))
        counts = {
            "responses": len(resp_ids),
            "skips": len(list(db.scalars(select(QuestionSkip.id).where(QuestionSkip.user_id == user.id)))),
            "masteries": len(list(db.scalars(select(SkillMastery.id).where(SkillMastery.user_id == user.id)))),
            "feedback_entries": len(list(db.scalars(select(UserFeedback.id).where(UserFeedback.user_id == user.id)))),
            "hints": len(list(db.scalars(select(HintUsage.id).where(HintUsage.user_id == user.id)))),
            "daily": len(list(db.scalars(select(DailyCompletion.id).where(DailyCompletion.user_id == user.id)))),
            "exercise_attempts": len(list(db.scalars(select(ExerciseAttempt.id).where(ExerciseAttempt.user_id == user.id)))),
            "exercise_help": len(list(db.scalars(select(ExerciseHelp.id).where(ExerciseHelp.user_id == user.id)))),
            "xp_events": len(list(db.scalars(select(XpEvent.id).where(XpEvent.user_id == user.id)))),
            "badges": len(list(db.scalars(select(UserBadge.id).where(UserBadge.user_id == user.id)))),
            "path_activity": len(list(db.scalars(select(PathActivity.id).where(PathActivity.user_id == user.id)))),
            "path_skips": len(list(db.scalars(select(PathSkip.id).where(PathSkip.user_id == user.id)))),
            "quizzes": len(list(db.scalars(select(QuizSession.id).where(QuizSession.user_id == user.id)))),
            "review_retries": len(list(db.scalars(select(ReviewRetry.id).where(ReviewRetry.user_id == user.id)))),
            "bookmarks": len(list(db.scalars(select(Bookmark.id).where(Bookmark.user_id == user.id)))),
            "settings": len(list(db.scalars(select(UserSettings.user_id).where(UserSettings.user_id == user.id)))),
        }
        if not body.dry_run:
            if resp_ids:
                db.execute(delete(Feedback).where(Feedback.response_id.in_(resp_ids)))
            # Quiz answers point at responses, so they go first.
            db.execute(delete(QuizAnswer).where(QuizAnswer.user_id == user.id))
            db.execute(delete(QuizSession).where(QuizSession.user_id == user.id))
            db.execute(delete(ReviewRetry).where(ReviewRetry.user_id == user.id))
            db.execute(delete(Response).where(Response.user_id == user.id))
            db.execute(delete(QuestionSkip).where(QuestionSkip.user_id == user.id))
            db.execute(delete(SkillMastery).where(SkillMastery.user_id == user.id))
            db.execute(delete(UserFeedback).where(UserFeedback.user_id == user.id))
            db.execute(delete(HintUsage).where(HintUsage.user_id == user.id))
            db.execute(delete(DailyCompletion).where(DailyCompletion.user_id == user.id))
            db.execute(delete(ExerciseAttempt).where(ExerciseAttempt.user_id == user.id))
            db.execute(delete(ExerciseHelp).where(ExerciseHelp.user_id == user.id))
            db.execute(delete(XpEvent).where(XpEvent.user_id == user.id))
            db.execute(delete(UserBadge).where(UserBadge.user_id == user.id))
            db.execute(delete(LearnerProfile).where(LearnerProfile.user_id == user.id))
            db.execute(delete(PathActivity).where(PathActivity.user_id == user.id))
            db.execute(delete(PathSkip).where(PathSkip.user_id == user.id))
            db.execute(delete(Bookmark).where(Bookmark.user_id == user.id))
            db.execute(delete(UserSettings).where(UserSettings.user_id == user.id))
            db.execute(delete(User).where(User.id == user.id))
        report.append({"identity": ident, "found": True, "name": user.display_name, **counts})
    if not body.dry_run:
        db.commit()
    return {"dry_run": body.dry_run, "users": report}
