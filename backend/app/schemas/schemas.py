"""Pydantic v2 schemas for the public API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Users ────────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Questions ────────────────────────────────────────────────────────────────


class QuestionOut(BaseModel):
    id: int
    domain_slug: str
    domain_name: str
    difficulty: str
    title: str
    scenario: str
    prompt: str

    model_config = {"from_attributes": True}


# ── Feedback / Responses ─────────────────────────────────────────────────────


class FallacyFinding(BaseModel):
    name: str
    explanation: str
    evidence_span: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ReasoningGap(BaseModel):
    description: str
    how_to_improve: str


class FeedbackPayload(BaseModel):
    """Structured feedback returned by any AI provider."""

    fallacies: list[FallacyFinding] = Field(default_factory=list)
    reasoning_gaps: list[ReasoningGap] = Field(default_factory=list)
    domain_scores: dict[str, float] = Field(default_factory=dict)
    suggestions: list[str] = Field(default_factory=list)
    overall_score: float = Field(ge=0.0, le=1.0, default=0.5)
    raw_explanation: str = ""
    provider_used: str = "heuristic"


class ResponseCreate(BaseModel):
    user_id: int
    question_id: int
    answer_text: str = Field(..., min_length=10, max_length=10000)


class ResponseOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    answer_text: str
    created_at: datetime
    feedback: FeedbackPayload

    model_config = {"from_attributes": True}


# ── Progress ─────────────────────────────────────────────────────────────────


class DomainProgress(BaseModel):
    domain_slug: str
    domain_name: str
    mastery: float
    attempts: int


class ProgressOut(BaseModel):
    user_id: int
    display_name: str
    domains: list[DomainProgress]
    total_responses: int
    average_mastery: float


# ── Generic ──────────────────────────────────────────────────────────────────


class HealthOut(BaseModel):
    status: str
    llm_configured: bool
    hf_available: bool
    database: str
    details: dict[str, Any] = Field(default_factory=dict)
