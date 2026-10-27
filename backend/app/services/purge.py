"""Delete one learner and everything they own.

Shared by the token-protected maintenance endpoint and the admin dashboard. A test walks
every table with a user column so a new table can't be forgotten here.
"""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.models import (
    Bookmark, DailyCompletion, ExerciseAttempt, ExerciseHelp, Feedback, FeedbackModeration, HintUsage,
    LearnerFlag, LearnerProfile, PathActivity, PathSkip, QuestionSkip, QuizAnswer, QuizSession, Response,
    ReviewRetry, SkillMastery, User, UserBadge, UserFeedback, UserSettings, XpEvent,
)

# Report name -> (model, user column). Order is the delete order: rows that point at other
# user rows go first (quiz answers -> responses, moderation -> feedback).
OWNED = [
    ("quiz_answers", QuizAnswer, QuizAnswer.user_id),
    ("quizzes", QuizSession, QuizSession.user_id),
    ("review_retries", ReviewRetry, ReviewRetry.user_id),
    ("responses", Response, Response.user_id),
    ("skips", QuestionSkip, QuestionSkip.user_id),
    ("masteries", SkillMastery, SkillMastery.user_id),
    ("feedback_entries", UserFeedback, UserFeedback.user_id),
    ("hints", HintUsage, HintUsage.user_id),
    ("daily", DailyCompletion, DailyCompletion.user_id),
    ("exercise_attempts", ExerciseAttempt, ExerciseAttempt.user_id),
    ("exercise_help", ExerciseHelp, ExerciseHelp.user_id),
    ("xp_events", XpEvent, XpEvent.user_id),
    ("badges", UserBadge, UserBadge.user_id),
    ("path_activity", PathActivity, PathActivity.user_id),
    ("path_skips", PathSkip, PathSkip.user_id),
    ("bookmarks", Bookmark, Bookmark.user_id),
    ("settings", UserSettings, UserSettings.user_id),
    ("flags", LearnerFlag, LearnerFlag.user_id),
    ("profile", LearnerProfile, LearnerProfile.user_id),
]


def counts(db: Session, user: User) -> dict[str, int]:
    out = {name: int(db.scalar(select(func.count()).select_from(model).where(col == user.id)) or 0) for name, model, col in OWNED}
    out["feedback_reviews"] = int(db.scalar(
        select(func.count()).select_from(FeedbackModeration)
        .where(FeedbackModeration.feedback_id.in_(select(UserFeedback.id).where(UserFeedback.user_id == user.id)))
    ) or 0)
    return out


def purge(db: Session, user: User, *, commit: bool = True) -> dict[str, int]:
    """Delete the learner and all their rows. Returns what was there."""
    report = counts(db, user)
    resp_ids = select(Response.id).where(Response.user_id == user.id)
    db.execute(delete(Feedback).where(Feedback.response_id.in_(resp_ids)))
    db.execute(delete(FeedbackModeration).where(
        FeedbackModeration.feedback_id.in_(select(UserFeedback.id).where(UserFeedback.user_id == user.id))))
    for _name, model, col in OWNED:
        db.execute(delete(model).where(col == user.id))
    db.execute(delete(User).where(User.id == user.id))
    if commit:
        db.commit()
    return report
