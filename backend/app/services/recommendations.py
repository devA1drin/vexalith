"""Personalised "Recommended for you" suggestions.

Built only from data the learner already produced (Elo mastery per skill and
the scores of their graded answers), so it is cheap, deterministic and needs no
AI call:

- **focus topics**: the weakest skills that have questions in the learner's
  language (fewest attempts first when mastery ties, so untried skills appear);
- **languages to revisit**: languages whose average score is below the
  learner's own overall average;
- **next questions**: one unseen question per focus topic, at the level the
  adaptive engine would pick for that skill.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import Feedback, Question, QuestionSkip, Response, SkillDomain, User
from app.schemas.schemas import (
    LanguageTip,
    QuestionOut,
    RecommendationsOut,
    TopicTip,
)
from app.services import adaptive
from app.services.learning import GENERAL, _diff, _question_out, ensure_user_masteries

MAX_TOPICS = 3
MAX_LANGUAGES = 2
LANG_NAMES = {
    "python": "Python", "javascript": "JavaScript", "php": "PHP", "cpp": "C++", "java": "Java",
    "html": "HTML", "css": "CSS", "general": "General",
}


def _favourite_language(db: Session, user: User) -> str:
    rows = (
        db.query(Question.language)
        .join(Response, Response.question_id == Question.id)
        .filter(Response.user_id == user.id, Question.language != GENERAL)
        .all()
    )
    if not rows:
        return "python"
    counts: dict[str, int] = {}
    for (lang,) in rows:
        counts[lang] = counts.get(lang, 0) + 1
    return max(sorted(counts), key=lambda k: counts[k])


def _topic_reason(mastery: float, attempts: int) -> str:
    if attempts == 0:
        return "You haven't tried this skill yet."
    if mastery < 0.4:
        return "Your weakest skill right now. A few beginner-friendly questions will lift it fastest."
    if mastery < 0.6:
        return "Still settling: practise it until it feels routine."
    return "Your lowest skill, though it is already solid. Keep it sharp."


def get_recommendations(db: Session, user: User, *, language: str | None = None) -> RecommendationsOut:
    language = language or _favourite_language(db, user)
    pool_langs = [GENERAL] if language == GENERAL else [language, GENERAL]
    questions = db.query(Question).filter(Question.language.in_(pool_langs)).all()
    domains = {d.id: d for d in db.query(SkillDomain).all()}
    if language in ("html", "css"):
        oop_id = next((d.id for d in domains.values() if d.slug == "oop"), None)
        questions = [q for q in questions if q.domain_id != oop_id] or questions
    available = {q.domain_id for q in questions}
    masteries = [m for m in ensure_user_masteries(db, user) if m.domain_id in available and m.domain_id in domains]

    # Weakest first; untried skills before tried ones at equal mastery band.
    masteries.sort(key=lambda m: (round(m.mastery, 2), m.attempts, domains[m.domain_id].slug))
    weakest = masteries[:MAX_TOPICS]

    seen = {r.question_id for r in db.query(Response.question_id).filter_by(user_id=user.id).all()}
    seen |= {r.question_id for r in db.query(QuestionSkip.question_id).filter_by(user_id=user.id).all()}

    topics: list[TopicTip] = []
    next_questions: list[QuestionOut] = []
    for m in weakest:
        d = domains[m.domain_id]
        level = adaptive.mastery_to_difficulty(m.mastery)
        topics.append(
            TopicTip(
                domain_slug=d.slug, domain_name=d.name, mastery=round(m.mastery, 4),
                attempts=m.attempts, suggested_difficulty=level, reason=_topic_reason(m.mastery, m.attempts),
            )
        )
        cands = [q for q in questions if q.domain_id == d.id and q.id not in seen]
        if not cands:
            continue
        # Prefer the chosen language over "general", then the suggested level,
        # then the closest level; ties broken by id so the list is stable.
        order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        cands.sort(key=lambda q: (
            q.language != language,
            abs(order.get(_diff(q), 1) - order[level]),
            q.id,
        ))
        next_questions.append(_question_out(cands[0], d))

    # Languages scoring below the learner's own average.
    scores: dict[str, list[float]] = {}
    for lang, score in (
        db.query(Question.language, Feedback.overall_score)
        .join(Response, Response.question_id == Question.id)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id)
        .all()
    ):
        scores.setdefault(lang, []).append(float(score or 0.0))
    langs: list[LanguageTip] = []
    if scores:
        overall = sum(sum(v) for v in scores.values()) / sum(len(v) for v in scores.values())
        ranked = sorted(scores.items(), key=lambda kv: (sum(kv[1]) / len(kv[1]), kv[0]))
        for lang, vals in ranked:
            avg = sum(vals) / len(vals)
            if len(scores) > 1 and avg >= overall:
                continue
            langs.append(
                LanguageTip(
                    language=lang, name=LANG_NAMES.get(lang, lang), attempts=len(vals),
                    average_score=round(avg, 4),
                    reason=f"Average {round(avg * 100)}% vs your overall {round(overall * 100)}%."
                    if len(scores) > 1 else f"Average {round(avg * 100)}% so far.",
                )
            )
            if len(langs) >= MAX_LANGUAGES:
                break

    if not seen:
        headline = "Start with the basics: here is where to begin."
    elif topics:
        headline = f"Focus on {topics[0].domain_name} next."
    else:
        headline = "You're all caught up. Try a harder level."
    return RecommendationsOut(
        language=language, headline=headline, topics=topics, languages=langs, next_questions=next_questions,
    )
