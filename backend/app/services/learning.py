"""Orchestration: next-question selection and response → feedback → mastery update."""

from __future__ import annotations

import os
import random

from sqlalchemy.orm import Session

from app.ai.provider import QuestionContext, get_ai_provider
from app.config import get_settings
from app.content.domains import DOMAINS, FUNDAMENTALS, GENERAL
from app.models.models import (
    Difficulty,
    Feedback,
    Question,
    QuestionSkip,
    Response,
    SkillDomain,
    SkillMastery,
    User,
)
from app.schemas.schemas import (
    DomainProgress,
    FeedbackPayload,
    FundamentalsStatus,
    LanguageProgress,
    ProgressOut,
    QuestionOut,
)
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


def _diff(q: Question) -> str:
    return q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty)


def _question_out(q: Question, domain: SkillDomain) -> QuestionOut:
    return QuestionOut(
        id=q.id,
        domain_slug=domain.slug,
        domain_name=domain.name,
        difficulty=_diff(q),
        language=q.language,
        title=q.title,
        code=q.code,
        prompt=q.prompt,
    )


def _question_context(q: Question, domain_slug: str) -> QuestionContext:
    return QuestionContext(
        title=q.title,
        language=q.language,
        code=q.code,
        prompt=q.prompt,
        domain_slug=domain_slug,
        difficulty=_diff(q),
        rubric=q.rubric,
    )


def maybe_generate_llm_question(
    db: Session,
    *,
    domain: SkillDomain,
    difficulty: str,
    language: str,
) -> Question | None:
    """Generate a fresh question via the LLM when LLM_GENERATE_QUESTIONS=1 (opt-in)."""
    flag = os.environ.get("LLM_GENERATE_QUESTIONS", "").lower()
    if flag not in {"1", "true", "yes"}:
        return None
    provider = get_ai_provider()
    if provider.name != "llm":
        return None
    generated = provider.generate_question(
        domain_slug=domain.slug, domain_name=domain.name, difficulty=difficulty, language=language
    )
    if not generated:
        return None
    q = Question(
        domain_id=domain.id,
        difficulty=Difficulty(difficulty),
        language=language,
        title=str(generated.get("title") or f"Generated: {domain.name}")[:256],
        code=str(generated["code"]),
        prompt=str(generated["prompt"]),
        rubric=generated.get("rubric"),
        source="llm",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def _recent_question_ids(db: Session, user: User, limit: int) -> list[int]:
    """Most recent answered or skipped question ids (newest first)."""
    answered = (
        db.query(Response.question_id, Response.created_at)
        .filter(Response.user_id == user.id)
        .order_by(Response.created_at.desc())
        .limit(limit)
        .all()
    )
    skipped = (
        db.query(QuestionSkip.question_id, QuestionSkip.created_at)
        .filter(QuestionSkip.user_id == user.id)
        .order_by(QuestionSkip.created_at.desc())
        .limit(limit)
        .all()
    )
    merged = sorted(list(answered) + list(skipped), key=lambda r: r[1], reverse=True)
    return [r[0] for r in merged[:limit]]


# ── Fundamentals onboarding ────────────────────────────────────────────────
# New learners start in Fundamentals at level 1 and stay there until they have
# answered FUND_MIN_ANSWERS fundamentals questions with a recent average score of
# at least FUND_PASS_AVG ("cleared"). Learners who already have real practice in
# other skills (EXPERIENCED_OTHER_ANSWERS answers) are never forced back. After
# that the weakest-first engine takes over and still revisits Fundamentals when
# it becomes the weakest skill.
FUND_MIN_ANSWERS = 5
FUND_PASS_AVG = 0.6
FUND_WINDOW = 5
EXPERIENCED_OTHER_ANSWERS = 3


def fundamentals_status(db: Session, user: User) -> FundamentalsStatus:
    rows = (
        db.query(SkillDomain.slug, Feedback.overall_score, Response.created_at)
        .join(Question, Question.domain_id == SkillDomain.id)
        .join(Response, Response.question_id == Question.id)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id)
        .order_by(Response.created_at.desc())
        .all()
    )
    fund = [float(r[1] or 0.0) for r in rows if r[0] == FUNDAMENTALS]
    other = sum(1 for r in rows if r[0] != FUNDAMENTALS)
    recent = fund[:FUND_WINDOW]
    avg = round(sum(recent) / len(recent), 4) if recent else 0.0
    cleared = len(fund) >= FUND_MIN_ANSWERS and avg >= FUND_PASS_AVG
    return FundamentalsStatus(
        answers=len(fund),
        strong_answers=sum(1 for x in fund if x >= FUND_PASS_AVG),
        recent_average=avg,
        cleared=cleared,
        experienced=other >= EXPERIENCED_OTHER_ANSWERS,
        min_answers=FUND_MIN_ANSWERS,
        pass_average=FUND_PASS_AVG,
    )


def fundamentals_level(status: FundamentalsStatus) -> str:
    """Level ladder inside Fundamentals: level 1 until 3 strong answers, level 2 until 6, then 3."""
    if status.strong_answers < 3:
        return "beginner"
    if status.strong_answers < 6:
        return "intermediate"
    return "advanced"


def get_next_question(
    db: Session,
    user: User,
    *,
    language: str = "python",
    exclude_ids: set[int] | None = None,
    avoid_domain_ids: set[int] | None = None,
    focus: str | None = None,
    rng: random.Random | None = None,
) -> QuestionOut:
    """Adaptive next question for the user in the chosen language.

    - weakest domain first (Elo mastery), difficulty band from mastery
    - never repeats the explicitly excluded / most recently seen questions
      (answered OR skipped) while alternatives exist
    - random choice among equally good candidates so Skip/Next feel fresh
    """
    settings = get_settings()
    rng = rng or random.Random()
    masteries = ensure_user_masteries(db, user)
    domains = {d.id: d for d in db.query(SkillDomain).all()}

    # Language pool: the chosen language plus language-agnostic questions
    # ("general": logic puzzles, prose algorithm problems). "general" alone is
    # also a valid selection.
    pool_langs = [GENERAL] if language == GENERAL else [language, GENERAL]
    all_in_lang = db.query(Question).filter(Question.language.in_(pool_langs)).all()
    if not all_in_lang:
        all_in_lang = db.query(Question).all()
    if not all_in_lang:
        raise LookupError("No questions available — seed the database.")

    # Only domains that actually have questions for this language are eligible
    # (e.g. no Big-O drills for HTML/CSS).
    available = {q.domain_id for q in all_in_lang}
    dm_list = [
        adaptive.DomainMastery(
            domain_id=m.domain_id,
            domain_slug=domains[m.domain_id].slug,
            mastery=m.mastery,
            attempts=m.attempts,
        )
        for m in masteries
        if m.domain_id in domains and m.domain_id in available
    ]
    # Fundamentals: explicit focus, or onboarding for new learners.
    fund_id = next((d.id for d in domains.values() if d.slug == FUNDAMENTALS), None)
    forced_level: str | None = None
    if fund_id is not None and fund_id in available:
        status = fundamentals_status(db, user)
        onboarding = not status.cleared and not status.experienced
        if focus == FUNDAMENTALS or onboarding:
            dm_list = [m for m in dm_list if m.domain_id == fund_id] or dm_list
            avoid_domain_ids = None
            forced_level = fundamentals_level(status)
    # After a skip, move on to a different skill when one is available.
    if avoid_domain_ids:
        others = [m for m in dm_list if m.domain_id not in avoid_domain_ids]
        dm_list = others or dm_list
    # Weakest skill first, in 0.1 mastery bands so tiny skip nudges don't pin the
    # learner to one skill; within a band prefer fewer attempts, then the skill
    # served least recently (round-robin), then random.
    recent_domains: dict[int, int] = {}
    recent_qids = _recent_question_ids(db, user, limit=30)
    if recent_qids:
        qdom = dict(db.query(Question.id, Question.domain_id).filter(Question.id.in_(recent_qids)).all())
        for pos, qid in enumerate(recent_qids):
            recent_domains.setdefault(qdom.get(qid, -1), pos)
    rng.shuffle(dm_list)
    weakest = min(
        dm_list,
        key=lambda m: (round(m.mastery * 10), m.attempts, -recent_domains.get(m.domain_id, 10_000)),
    )
    preferred = forced_level or adaptive.mastery_to_difficulty(
        weakest.mastery, offset=settings.target_difficulty_offset
    )
    domain = domains[weakest.domain_id]

    if language != GENERAL and forced_level is None:
        generated = maybe_generate_llm_question(db, domain=domain, difficulty=preferred, language=language)
        if generated:
            return _question_out(generated, domain)

    answered_ids = {r.question_id for r in db.query(Response.question_id).filter_by(user_id=user.id).all()}
    skipped_ids = {r.question_id for r in db.query(QuestionSkip.question_id).filter_by(user_id=user.id).all()}
    seen_ids = answered_ids | skipped_ids
    recent = set(_recent_question_ids(db, user, limit=12)) | set(exclude_ids or set())

    def choose(pool: list[Question]) -> Question | None:
        fresh = [q for q in pool if q.id not in recent]
        if not fresh:
            return None
        cands = [{"id": q.id, "difficulty": _diff(q), "obj": q} for q in fresh]
        rng.shuffle(cands)
        picked = adaptive.pick_question(candidates=cands, seen_ids=seen_ids, preferred_difficulty=preferred)
        return picked["obj"] if picked else None

    in_domain = [q for q in all_in_lang if q.domain_id == domain.id]
    q = choose(in_domain) or (None if forced_level else choose(all_in_lang))
    if q is None and forced_level:
        # Every fundamentals question is "recent": reuse the least recent one.
        pool = [x for x in in_domain if x.id not in (exclude_ids or set())] or in_domain
        q = rng.choice(pool)
    if q is None:
        # Everything is "recent": at least avoid the explicitly excluded ids.
        pool = [x for x in all_in_lang if x.id not in (exclude_ids or set())] or all_in_lang
        q = rng.choice(pool)
    d = domains.get(q.domain_id) or db.get(SkillDomain, q.domain_id)
    assert d is not None
    return _question_out(q, d)


SKIP_MASTERY_NUDGE = 0.01  # skipping is not failing: tiny nudge, attempts unchanged


def skip_question(db: Session, *, user: User, question: Question) -> None:
    """Record a skip. Mastery decreases only slightly; attempts are not counted."""
    db.add(QuestionSkip(user_id=user.id, question_id=question.id))
    ensure_user_masteries(db, user)
    row = db.query(SkillMastery).filter_by(user_id=user.id, domain_id=question.domain_id).one()
    row.mastery = round(max(0.0, row.mastery - SKIP_MASTERY_NUDGE), 4)
    db.commit()


def submit_response(
    db: Session,
    *,
    user: User,
    question: Question,
    answer_text: str,
) -> tuple[Response, FeedbackPayload]:
    """Persist response, run AI feedback, update mastery (Elo)."""
    settings = get_settings()
    provider = get_ai_provider()
    domain = db.get(SkillDomain, question.domain_id)
    domain_slug = domain.slug if domain else "unknown"

    payload = provider.evaluate_response(question=_question_context(question, domain_slug), answer=answer_text)

    response = Response(user_id=user.id, question_id=question.id, answer_text=answer_text)
    db.add(response)
    db.flush()

    db.add(
        Feedback(
            response_id=response.id,
            misconceptions=[f.model_dump() for f in payload.misconceptions],
            reasoning_gaps=[g.model_dump() for g in payload.reasoning_gaps],
            domain_scores=payload.domain_scores,
            suggestions=payload.suggestions,
            overall_score=payload.overall_score,
            provider_used=payload.provider_used,
            raw_explanation=payload.raw_explanation,
            details={
                "verdict": payload.verdict,
                "correctness_score": payload.correctness_score,
                "reasoning_score": payload.reasoning_score,
                "strengths": payload.strengths,
                "missed_concepts": payload.missed_concepts,
                "reference_answer": payload.reference_answer,
            },
        )
    )

    ensure_user_masteries(db, user)
    mastery_row = db.query(SkillMastery).filter_by(user_id=user.id, domain_id=question.domain_id).one()
    score = payload.domain_scores.get(domain_slug, payload.overall_score)
    mastery_row.mastery = adaptive.update_mastery(
        mastery_row.mastery, float(score), _diff(question), k=settings.mastery_k
    )
    mastery_row.attempts += 1

    db.commit()
    db.refresh(response)
    return response, payload


def get_progress(db: Session, user: User) -> ProgressOut:
    masteries = ensure_user_masteries(db, user)
    domains = {d.id: d for d in db.query(SkillDomain).all()}
    total = db.query(Response).filter_by(user_id=user.id).count()
    skips = db.query(QuestionSkip).filter_by(user_id=user.id).count()
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
    order = {d["slug"]: i for i, d in enumerate(DOMAINS)}
    domain_rows.sort(key=lambda x: (order.get(x.domain_slug, 99), x.domain_slug))
    avg = (
        sum(r.mastery for r in domain_rows) / len(domain_rows) if domain_rows else 0.0
    )
    # Per-language breakdown: attempts and mean overall score.
    lang_rows: dict[str, list[float]] = {}
    for lang, score in (
        db.query(Question.language, Feedback.overall_score)
        .join(Response, Response.question_id == Question.id)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id)
        .all()
    ):
        lang_rows.setdefault(lang, []).append(float(score or 0.0))
    languages = [
        LanguageProgress(language=k, attempts=len(v), average_score=round(sum(v) / len(v), 4))
        for k, v in sorted(lang_rows.items(), key=lambda kv: -len(kv[1]))
    ]
    return ProgressOut(
        user_id=user.id,
        display_name=user.display_name,
        domains=domain_rows,
        languages=languages,
        fundamentals=fundamentals_status(db, user),
        total_responses=total,
        total_skips=skips,
        average_mastery=round(avg, 4),
    )
