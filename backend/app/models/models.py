"""
SQLAlchemy ORM models for the Adaptive Learning MVP.

Domain model overview
---------------------
User ──< SkillMastery >── SkillDomain
User ──< Response >── Question ── SkillDomain
User ──< QuestionSkip >── Question
User ──< UserFeedback            (app feedback submitted by signed-in users)
User ──< HintUsage >── Question  (progressive hints revealed while answering)
User ──< DailyCompletion >── Question (daily challenge done, one row per Manila day)
Response ── Feedback (1:1)       (AI feedback on an answer)
User ──< ExerciseAttempt          (browser coding exercise runs; code never runs on the server)
AppMeta                          (schema version for safe re-seeding)
User ──1 UserSettings, User ──< Bookmark   (profile choices and saved items)
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Difficulty(str, enum.Enum):
    """Question difficulty tiers mapped roughly to mastery bands."""

    beginner = "beginner"  # mastery ~0.0–0.35
    intermediate = "intermediate"  # ~0.35–0.65
    advanced = "advanced"  # ~0.65–1.0


class SkillDomain(Base):
    """A programming-reasoning skill area that mastery is tracked against."""

    __tablename__ = "skill_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")

    questions: Mapped[list[Question]] = relationship(back_populates="domain")
    masteries: Mapped[list[SkillMastery]] = relationship(back_populates="domain")


class User(Base):
    """Learner identity, linked to an OAuth account (GitHub / Google) via Auth.js."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("auth_provider", "provider_account_id", name="uq_user_provider_account"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_provider: Mapped[str] = mapped_column(String(32))
    provider_account_id: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128))
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    responses: Mapped[list[Response]] = relationship(back_populates="user")
    masteries: Mapped[list[SkillMastery]] = relationship(back_populates="user")


class Question(Base):
    """A code snippet + open-ended prompt targeting one skill domain and language."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("skill_domains.id"), index=True)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty_enum"),
        default=Difficulty.intermediate,
    )
    language: Mapped[str] = mapped_column(String(32), default="python", index=True)
    title: Mapped[str] = mapped_column(String(256))
    code: Mapped[str] = mapped_column(Text, default="")
    prompt: Mapped[str] = mapped_column(Text)
    # Grading rubric: {concepts: [...], misconceptions: [...], reference_answer: str}
    rubric: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="seed")  # seed | llm
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    domain: Mapped[SkillDomain] = relationship(back_populates="questions")
    responses: Mapped[list[Response]] = relationship(back_populates="question")


class Response(Base):
    """A learner's free-text answer to a question."""

    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    answer_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped[User] = relationship(back_populates="responses")
    question: Mapped[Question] = relationship(back_populates="responses")
    feedback: Mapped[Feedback | None] = relationship(
        back_populates="response", uselist=False
    )


class Feedback(Base):
    """Explainable AI evaluation of a response."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    response_id: Mapped[int] = mapped_column(
        ForeignKey("responses.id"), unique=True, index=True
    )
    # Structured JSON payloads (see schemas.FeedbackPayload).
    misconceptions: Mapped[list] = mapped_column(JSON, default=list)
    reasoning_gaps: Mapped[list] = mapped_column(JSON, default=list)
    domain_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    suggestions: Mapped[list] = mapped_column(JSON, default=list)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    provider_used: Mapped[str] = mapped_column(String(32), default="heuristic")
    raw_explanation: Mapped[str] = mapped_column(Text, default="")
    # Programming-specific details: verdict, correctness/reasoning scores, strengths, ...
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    response: Mapped[Response] = relationship(back_populates="feedback")


class SkillMastery(Base):
    """Per-user, per-domain mastery estimate in [0, 1]."""

    __tablename__ = "skill_masteries"
    __table_args__ = (
        UniqueConstraint("user_id", "domain_id", name="uq_user_domain_mastery"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("skill_domains.id"), index=True)
    mastery: Mapped[float] = mapped_column(Float, default=0.5)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    user: Mapped[User] = relationship(back_populates="masteries")
    domain: Mapped[SkillDomain] = relationship(back_populates="masteries")


class QuestionSkip(Base):
    """A learner skipped a question (counts as 'seen' for selection, tiny mastery nudge)."""

    __tablename__ = "question_skips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class HintUsage(Base):
    """One hint level revealed by a learner for a question (counts towards a small score penalty)."""

    __tablename__ = "hint_usages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    level: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DailyCompletion(Base):
    """A learner answered that day's daily challenge (day = Asia/Manila calendar date)."""

    __tablename__ = "daily_completions"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_daily_user_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD in Asia/Manila
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    score: Mapped[float] = mapped_column(Float, default=0.0)  # best score that day
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserFeedback(Base):
    """Product feedback submitted by a signed-in user."""

    __tablename__ = "user_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(Text)
    page_context: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )

    user: Mapped[User] = relationship()


class ExerciseAttempt(Base):
    """A run of the hidden + visible tests for a browser coding exercise (code runs client-side only)."""

    __tablename__ = "exercise_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    slug: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(32))
    passed: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    code: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class ExerciseHelp(Base):
    """Help a learner opened on a coding exercise: a hint level, or the reference solution.

    ``before_pass`` is true when it was opened before the learner had passed every test,
    which is what marks an exercise as "solved with help". New table, so it's additive.
    """

    __tablename__ = "exercise_help"
    __table_args__ = (UniqueConstraint("user_id", "slug", "kind", "level", name="uq_exercise_help"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    slug: Mapped[str] = mapped_column(String(64), index=True)
    kind: Mapped[str] = mapped_column(String(16))  # "hint" or "solution"
    level: Mapped[int] = mapped_column(Integer, default=0)  # hint level 1..3; 0 for the solution
    before_pass: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class AppMeta(Base):
    """Key/value metadata (e.g. schema_version)."""

    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))


# --- XP, badges and leaderboard (new tables, so they're additive; see app/services/xp.py) ---


class XpEvent(Base):
    """One XP award. ``key`` makes each award happen once (e.g. "answer:12", "daily:2026-10-20").

    ``created_at`` is when the learner did the thing (so XP from older history lands in the
    right week). ``retro`` marks awards counted from history the first time XP was turned on.
    ``notified`` flips once the browser has shown the learner a toast for it.
    """

    __tablename__ = "xp_events"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_xp_event_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    key: Mapped[str] = mapped_column(String(96))
    kind: Mapped[str] = mapped_column(String(24))  # answer | exercise | daily | streak
    amount: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(200), default="")
    retro: Mapped[int] = mapped_column(Integer, default=0)
    notified: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserBadge(Base):
    """A badge a learner has earned (badge keys are defined in app/services/xp.py)."""

    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge", name="uq_user_badge"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    badge: Mapped[str] = mapped_column(String(32))
    retro: Mapped[int] = mapped_column(Integer, default=0)
    notified: Mapped[int] = mapped_column(Integer, default=0)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class LearnerProfile(Base):
    """How a learner appears on the leaderboard. Never holds an email.

    ``handle`` is a generated, non-identifying name (e.g. "Swift Parser 42").
    ``visibility``: "handle" (default), "name" (their display name, opt-in),
    "anonymous" (shown as "Anonymous learner") or "hidden" (left off the board).
    """

    __tablename__ = "learner_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    handle: Mapped[str] = mapped_column(String(40), unique=True)
    visibility: Mapped[str] = mapped_column(String(16), default="handle")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


# --- Learning paths (new tables, so they're additive; see app/services/paths.py) ---
# Progress itself is worked out from answers and exercise runs; these only remember
# where the learner was last and which steps they chose to skip ahead to.


class PathActivity(Base):
    """The step a learner last opened in a path, for "Continue where you left off"."""

    __tablename__ = "path_activity"
    __table_args__ = (UniqueConstraint("user_id", "path", name="uq_path_activity"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    path: Mapped[str] = mapped_column(String(40))
    step: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class PathSkip(Base):
    """A locked step the learner chose to open early ("skip ahead")."""

    __tablename__ = "path_skips"
    __table_args__ = (UniqueConstraint("user_id", "path", "step", name="uq_path_skip"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    path: Mapped[str] = mapped_column(String(40))
    step: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# --- Mistake review and timed quizzes (new tables, additive; see services/review.py, services/quiz.py) ---
# Mistakes themselves are worked out from answers and exercise runs. These tables only hold
# what history can't: a quiz's question list and server-side clock, and "retry" markers.


class QuizSession(Base):
    """One timed quiz. The clock lives here (started_at/deadline_at), so a refresh never resets it."""

    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    scope: Mapped[str] = mapped_column(String(16))  # topic | language | path | mixed
    scope_value: Mapped[str] = mapped_column(String(64), default="")
    scope_label: Mapped[str] = mapped_column(String(120), default="")
    length: Mapped[int] = mapped_column(Integer)
    time_limit_s: Mapped[int] = mapped_column(Integer)
    instant: Mapped[int] = mapped_column(Integer, default=0)  # 1 = feedback after each question
    question_ids: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)  # active | finished
    ended_by: Mapped[str] = mapped_column(String(16), default="")  # done | time | ended
    correct: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)  # correct / length
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class QuizAnswer(Base):
    """One question slot in a quiz: the answer given (if any) and the graded response."""

    __tablename__ = "quiz_answers"
    __table_args__ = (UniqueConstraint("quiz_id", "position", name="uq_quiz_answer"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz_sessions.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_text: Mapped[str] = mapped_column(Text, default="")
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    response_id: Mapped[int | None] = mapped_column(ForeignKey("responses.id"), nullable=True, index=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReviewRetry(Base):
    """The learner retried an item from Review ("q:<question id>" or "x:<exercise slug>").

    A fix only earns its XP when it follows one of these, so answering wrong on purpose and
    then right in normal practice pays nothing extra.
    """

    __tablename__ = "review_retries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# --- Profile and bookmarks (new tables, additive; see services/profile.py, services/bookmarks.py) ---


class UserSettings(Base):
    """What a learner chose on their profile page. Never holds an email.

    ``display_name`` overrides the name from GitHub/Google (which is refreshed on every
    sign-in, so it can't be edited in place). Empty means "use the sign-in name".
    The leaderboard handle and visibility stay in LearnerProfile.
    """

    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(40), default="")
    avatar: Mapped[str] = mapped_column(String(32), default="")
    bio: Mapped[str] = mapped_column(String(200), default="")
    practice_languages: Mapped[list] = mapped_column(JSON, default=list)
    answer_language: Mapped[str] = mapped_column(String(8), default="en")  # en | fil | taglish
    quiz_defaults: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Bookmark(Base):
    """A saved question ("q:<id>") or coding exercise ("x:<slug>"), with an optional short note."""

    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "item", name="uq_bookmark_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item: Mapped[str] = mapped_column(String(80))
    note: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


# ----------------------------------------------------------------------------- admin dashboard (additive)

class QuestionEdit(Base):
    """An admin's change to a question. Seeding rewrites questions from code on every start,
    so edits live here and are applied again after each seed."""

    __tablename__ = "question_edits"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), primary_key=True)
    question_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # the prompt without its task line
    reference_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_idea: Mapped[str | None] = mapped_column(Text, nullable=True)
    hidden: Mapped[int] = mapped_column(Integer, default=0, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class LearnerFlag(Base):
    """Admin-set flags on a learner (separate from the learner's own choices)."""

    __tablename__ = "learner_flags"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    board_hidden: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class FeedbackModeration(Base):
    """Review state of one piece of product feedback."""

    __tablename__ = "feedback_moderation"

    feedback_id: Mapped[int] = mapped_column(ForeignKey("user_feedback.id"), primary_key=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hidden: Mapped[int] = mapped_column(Integer, default=0, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class AdminAudit(Base):
    """One admin action. The actor is kept by id and name (no foreign key) so the log
    outlives deleted accounts; it never stores emails."""

    __tablename__ = "admin_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int] = mapped_column(Integer, index=True)
    actor_name: Mapped[str] = mapped_column(String(80), default="")
    action: Mapped[str] = mapped_column(String(40), index=True)
    target: Mapped[str] = mapped_column(String(120), default="")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
