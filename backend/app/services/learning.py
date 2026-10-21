"""Orchestration: next-question selection and response → feedback → mastery update."""

from __future__ import annotations

import os

from sqlalchemy.orm import Session

from app.ai.provider import get_ai_provider
from app.config import get_settings
from app.models.models import (
    Difficulty,
    Feedback,
    Question,
    Response,
    SkillDomain,
    SkillMastery,
    User,
)
from app.schemas.schemas import FeedbackPayload, ProgressOut, DomainProgress, QuestionOut
from app.services import adaptive


def ensure_user_masteries(db: Session, user: User) -> list[SkillMastery]:
    """Create SkillMastery rows for every domain if missing."""
    settings = get_settings()
    domains = db.query(SkillDomain).all()
    existing = {
        m.domain_id: m
        for m in db.query(SkillMastery).filter_by(user_id=user.id).all()
    }
    created = False
    for domain in domains:
        if domain.id not in existing:
            m = SkillMastery(
                user_id=user.id,
                domain_id=domain.id,
                mastery=settings.initial_mastery,
                attempts=0,
            )
            db.add(m)
            existing[domain.id] = m
            created = True
    if created:
        db.commit()
        for m in existing.values():
            db.refresh(m)
    return list(existing.values())


def _question_out(q: Question, domain: SkillDomain) -> QuestionOut:
    return QuestionOut(
        id=q.id,
        domain_slug=domain.slug,
        domain_name=domain.name,
        difficulty=q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
        title=q.title,
        scenario=q.scenario,
        prompt=q.prompt,
    )


def maybe_generate_llm_question(
    db: Session,
    *,
    domain: SkillDomain,
    difficulty: str,
) -> Question | None:
    """
    Ask the LLM to create a question when LLM_GENERATE_QUESTIONS=1 (or true).
    Off by default so /next stays fast and uses the seeded bank.
    """
    flag = os.environ.get("LLM_GENERATE_QUESTIONS", "").lower()
    if flag not in {"1", "true", "yes"}:
        return None
    provider = get_ai_provider()
    if provider.name != "llm":
        return None
    generated = provider.generate_question(
        domain_slug=domain.slug,
        domain_name=domain.name,
        difficulty=difficulty,
    )
    if not generated or not generated.get("scenario") or not generated.get("prompt"):
        return None
    q = Question(
        domain_id=domain.id,
        difficulty=Difficulty(difficulty),
        title=str(generated.get("title") or f"Generated: {domain.slug}"),
        scenario=str(generated["scenario"]),
        prompt=str(generated["prompt"]),
        expected_signals=generated.get("expected_signals"),
        source="llm",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def get_next_question(db: Session, user: User) -> QuestionOut:
    """Adaptive next question for the user (seed bank by default)."""
    settings = get_settings()
    masteries = ensure_user_masteries(db, user)
    domains = {d.id: d for d in db.query(SkillDomain).all()}

    dm_list = [
        adaptive.DomainMastery(
            domain_id=m.domain_id,
            domain_slug=domains[m.domain_id].slug,
            mastery=m.mastery,
            attempts=m.attempts,
        )
        for m in masteries
        if m.domain_id in domains
    ]
    weakest = adaptive.select_weakest_domain(dm_list)
    preferred = adaptive.mastery_to_difficulty(
        weakest.mastery, offset=settings.target_difficulty_offset
    )
    domain = domains[weakest.domain_id]

    # Optional LLM generation (explicit opt-in).
    generated = maybe_generate_llm_question(db, domain=domain, difficulty=preferred)
    if generated:
        return _question_out(generated, domain)

    questions = (
        db.query(Question)
        .filter(Question.domain_id == weakest.domain_id)
        .all()
    )
    if not questions:
        questions = db.query(Question).all()

    seen_ids = {
        r.question_id
        for r in db.query(Response).filter_by(user_id=user.id).all()
    }
    candidates = [
        {
            "id": q.id,
            "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
            "obj": q,
        }
        for q in questions
    ]
    picked = adaptive.pick_question(
        candidates=candidates,
        seen_ids=seen_ids,
        preferred_difficulty=preferred,
    )
    if not picked:
        raise LookupError("No questions available — seed the database.")

    q: Question = picked["obj"]
    d = domains.get(q.domain_id) or db.get(SkillDomain, q.domain_id)
    assert d is not None
    return _question_out(q, d)


def submit_response(
    db: Session,
    *,
    user: User,
    question: Question,
    answer_text: str,
) -> tuple[Response, FeedbackPayload]:
    """Persist response, run AI feedback, update mastery."""
    settings = get_settings()
    provider = get_ai_provider()
    domain = db.get(SkillDomain, question.domain_id)
    domain_slug = domain.slug if domain else "unknown"

    payload = provider.evaluate_response(
        scenario=question.scenario,
        prompt=question.prompt,
        answer=answer_text,
        domain_slug=domain_slug,
        expected_signals=question.expected_signals,
    )

    response = Response(
        user_id=user.id,
        question_id=question.id,
        answer_text=answer_text,
    )
    db.add(response)
    db.flush()

    fb = Feedback(
        response_id=response.id,
        fallacies=[f.model_dump() for f in payload.fallacies],
        reasoning_gaps=[g.model_dump() for g in payload.reasoning_gaps],
        domain_scores=payload.domain_scores,
        suggestions=payload.suggestions,
        overall_score=payload.overall_score,
        provider_used=payload.provider_used,
        raw_explanation=payload.raw_explanation,
    )
    db.add(fb)

    ensure_user_masteries(db, user)
    mastery_row = (
        db.query(SkillMastery)
        .filter_by(user_id=user.id, domain_id=question.domain_id)
        .one()
    )
    score = payload.domain_scores.get(domain_slug, payload.overall_score)
    diff = question.difficulty.value if hasattr(question.difficulty, "value") else str(question.difficulty)
    mastery_row.mastery = adaptive.update_mastery(
        mastery_row.mastery,
        float(score),
        diff,
        k=settings.mastery_k,
    )
    mastery_row.attempts += 1

    db.commit()
    db.refresh(response)
    return response, payload


def get_progress(db: Session, user: User) -> ProgressOut:
    masteries = ensure_user_masteries(db, user)
    domains = {d.id: d for d in db.query(SkillDomain).all()}
    total = db.query(Response).filter_by(user_id=user.id).count()
    domain_rows = []
    for m in masteries:
        d = domains.get(m.domain_id)
        if not d:
            continue
        domain_rows.append(
            DomainProgress(
                domain_slug=d.slug,
                domain_name=d.name,
                mastery=m.mastery,
                attempts=m.attempts,
            )
        )
    domain_rows.sort(key=lambda x: x.domain_slug)
    avg = (
        sum(r.mastery for r in domain_rows) / len(domain_rows) if domain_rows else 0.0
    )
    return ProgressOut(
        user_id=user.id,
        display_name=user.display_name,
        domains=domain_rows,
        total_responses=total,
        average_mastery=round(avg, 4),
    )
