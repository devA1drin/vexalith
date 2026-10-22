"""Daily challenge: one question per day, the same for everyone.

The "day" is the calendar date in Asia/Manila. The Philippines has used UTC+8
all year round since 1978 (no daylight saving), so a fixed offset is exact and
needs no tz database on the server.

Picking is deterministic. The day number (days since ``EPOCH``) chooses the
language (a new one every day), and every 7 days the skill moves on for each
language. Inside that pool, sha256 of the date string picks the question from a
stably sorted list. Every server instance, and every learner, gets the same
question for the same date.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.models import DailyCompletion, Question, SkillDomain, User

MANILA = timezone(timedelta(hours=8), "Asia/Manila")
EPOCH = date(2026, 1, 1)
ROTATION = ["python", "javascript", "cpp", "general", "php", "css", "html"]
DOMAIN_ORDER = [
    "fundamentals", "code_tracing", "debugging", "algorithmic_thinking", "edge_cases_testing",
    "code_review_design", "data_structures", "algorithms", "logic_problems",
]


def manila_today(now: datetime | None = None) -> date:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(MANILA).date()


def next_reset(now: datetime | None = None) -> datetime:
    """Midnight in Manila after ``now`` (as an aware UTC datetime)."""
    day = manila_today(now) + timedelta(days=1)
    return datetime(day.year, day.month, day.day, tzinfo=MANILA).astimezone(timezone.utc)


def _diff(q: Question) -> str:
    return q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty)


@dataclass
class DailyPick:
    day: date
    question: Question
    domain: SkillDomain


def pick_for(db: Session, day: date) -> DailyPick:
    """The daily challenge for ``day`` (deterministic, same for everyone)."""
    idx = (day - EPOCH).days
    domains = {d.id: d for d in db.query(SkillDomain).all()}
    seeds = db.query(Question).filter(Question.source == "seed").all() or db.query(Question).all()
    if not seeds:
        raise LookupError("No questions available — seed the database.")
    language = ROTATION[idx % len(ROTATION)]
    in_lang = [q for q in seeds if q.language == language] or seeds
    slugs = {domains[q.domain_id].slug for q in in_lang if q.domain_id in domains}
    topics = [s for s in DOMAIN_ORDER if s in slugs] + sorted(slugs - set(DOMAIN_ORDER))
    topic = topics[(idx // len(ROTATION)) % len(topics)]
    pool = [q for q in in_lang if domains[q.domain_id].slug == topic]
    pool.sort(key=lambda q: (_diff(q), q.title, q.id))
    h = int(hashlib.sha256(day.isoformat().encode()).hexdigest(), 16)
    q = pool[h % len(pool)]
    return DailyPick(day=day, question=q, domain=domains[q.domain_id])


def record_if_daily(db: Session, user: User, question: Question, score: float, now: datetime | None = None) -> bool:
    """Mark today's daily challenge done when ``question`` is today's pick. Keeps the best score."""
    day = manila_today(now)
    if pick_for(db, day).question.id != question.id:
        return False
    key = day.isoformat()
    row = db.query(DailyCompletion).filter_by(user_id=user.id, day=key).one_or_none()
    if row is None:
        db.add(DailyCompletion(user_id=user.id, day=key, question_id=question.id, score=score))
    elif score > row.score:
        row.score = score
    return True


def streaks(days: set[date], today: date) -> tuple[int, int]:
    """(current, best) runs of consecutive days.

    The current streak is still alive if the last completed day is today or
    yesterday (you have until Manila midnight to keep it going).
    """
    best = run = 0
    prev: date | None = None
    for d in sorted(days):
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        best = max(best, run)
        prev = d
    current = 0
    cursor = today if today in days else today - timedelta(days=1)
    while cursor in days:
        current += 1
        cursor -= timedelta(days=1)
    return current, best


def user_days(db: Session, user: User) -> dict[date, float]:
    rows = db.query(DailyCompletion.day, DailyCompletion.score).filter_by(user_id=user.id).all()
    return {date.fromisoformat(d): float(s or 0.0) for d, s in rows}
