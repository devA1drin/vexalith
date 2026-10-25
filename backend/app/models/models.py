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
