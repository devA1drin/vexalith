"""
SQLAlchemy ORM models for the Adaptive Learning MVP.

Domain model overview
---------------------
User ──< SkillMastery >── SkillDomain
User ──< Response >── Question ── SkillDomain
Response ── Feedback (1:1)
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
    """A critical-thinking skill area that mastery is tracked against."""

    __tablename__ = "skill_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")

    questions: Mapped[list[Question]] = relationship(back_populates="domain")
    masteries: Mapped[list[SkillMastery]] = relationship(back_populates="domain")


class User(Base):
    """Learner identity. MVP uses a simple display name (no auth)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    responses: Mapped[list[Response]] = relationship(back_populates="user")
    masteries: Mapped[list[SkillMastery]] = relationship(back_populates="user")


class Question(Base):
    """A scenario + open-ended prompt targeting one skill domain."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("skill_domains.id"), index=True)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty_enum"),
        default=Difficulty.intermediate,
    )
    title: Mapped[str] = mapped_column(String(256))
    scenario: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text)
    # Optional teacher-facing hints used by offline evaluators.
    expected_signals: Mapped[dict | None] = mapped_column(JSON, nullable=True)
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
    fallacies: Mapped[list] = mapped_column(JSON, default=list)
    reasoning_gaps: Mapped[list] = mapped_column(JSON, default=list)
    domain_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    suggestions: Mapped[list] = mapped_column(JSON, default=list)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    provider_used: Mapped[str] = mapped_column(String(32), default="heuristic")
    raw_explanation: Mapped[str] = mapped_column(Text, default="")
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
