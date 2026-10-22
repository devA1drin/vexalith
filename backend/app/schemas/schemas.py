"""Pydantic v2 schemas for the public API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ── Users ────────────────────────────────────────────────────────────────────


class UserOut(BaseModel):
    id: int
    display_name: str
    email: str | None = None
    avatar_url: str | None = None
    auth_provider: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Questions ────────────────────────────────────────────────────────────────


class QuestionOut(BaseModel):
    id: int
    domain_slug: str
    domain_name: str
    difficulty: str
    language: str
    title: str
    code: str
    prompt: str


class SkipOut(BaseModel):
    skipped_question_id: int
    next_question: QuestionOut


# ── Feedback on answers ──────────────────────────────────────────────────────


class Finding(BaseModel):
    """A misconception / issue spotted in the learner's explanation."""

    name: str
    explanation: str
    evidence_span: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


# Backwards-compatible alias (older code referred to fallacies).
FallacyFinding = Finding


class ReasoningGap(BaseModel):
    description: str
    how_to_improve: str


class FeedbackPayload(BaseModel):
    """Structured, explainable feedback returned by any grader."""

    verdict: Literal["correct", "partially_correct", "incorrect"] = "partially_correct"
    correctness_score: float = Field(ge=0.0, le=1.0, default=0.5)
    reasoning_score: float = Field(ge=0.0, le=1.0, default=0.5)
    overall_score: float = Field(ge=0.0, le=1.0, default=0.5)
    strengths: list[str] = Field(default_factory=list)
    missed_concepts: list[str] = Field(default_factory=list)
    misconceptions: list[Finding] = Field(default_factory=list)
    reasoning_gaps: list[ReasoningGap] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    domain_scores: dict[str, float] = Field(default_factory=dict)
    reference_answer: str | None = None
    raw_explanation: str = ""
    provider_used: str = "heuristic"


class ResponseCreate(BaseModel):
    question_id: int
    answer_text: str = Field(..., min_length=10, max_length=10000)


class ResponseOut(BaseModel):
    id: int
    question_id: int
    answer_text: str
    created_at: datetime
    feedback: FeedbackPayload


# ── Progress ─────────────────────────────────────────────────────────────────


class DomainProgress(BaseModel):
    domain_slug: str
    domain_name: str
    mastery: float
    attempts: int


class LanguageProgress(BaseModel):
    language: str
    attempts: int
    average_score: float


class ProgressOut(BaseModel):
    user_id: int
    display_name: str
    domains: list[DomainProgress]
    languages: list[LanguageProgress] = []
    total_responses: int
    total_skips: int = 0
    average_mastery: float


# ── Product feedback ─────────────────────────────────────────────────────────

FeedbackCategory = Literal["bug", "feature_request", "question_content", "other"]


class UserFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    category: FeedbackCategory
    message: str = Field(..., min_length=5, max_length=2000)
    page_context: str | None = Field(default=None, max_length=300)

    @field_validator("message")
    @classmethod
    def _clean_message(cls, v: str) -> str:
        v = v.replace("\x00", "").strip()
        if len(v) < 5:
            raise ValueError("message must contain at least 5 non-space characters")
        return v

    @field_validator("page_context")
    @classmethod
    def _clean_context(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.replace("\x00", "").strip()
        return v or None


class UserFeedbackOut(BaseModel):
    id: int
    rating: int
    category: str
    message: str
    page_context: str | None
    created_at: datetime


class PublicFeedbackOut(BaseModel):
    """Public wall entry — never includes email."""

    id: int
    author_name: str
    author_avatar_url: str | None
    rating: int
    category: str
    message: str
    created_at: datetime


# ── Generic ──────────────────────────────────────────────────────────────────


class HealthOut(BaseModel):
    status: str
    llm_configured: bool
    auth_configured: bool
    database: str
    question_count: int | None = None
    details: dict[str, Any] = Field(default_factory=dict)
