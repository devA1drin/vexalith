"""Mistake review: questions answered wrong (or only partly right) and coding exercises
failed or solved with help, worked out from the learner's existing history.

Every item follows the same small state machine, replayed from history in time order:

    wrong answer / failed run      -> open   ("To fix")
    right answer while open        -> fixed  (+FIX_XP once per item, ever, when retried from Review)
    right answer >= CONFIRM_DAYS
      after the fix                -> stuck  (confirmed; it leaves for good)
    wrong answer while fixed/stuck -> open again

A fixed item comes back once as "Check again" when CONFIRM_DAYS have passed.
Any correct answer takes an item off the list, but the fix XP (and Second Look progress)
only counts when the learner retried it from Review (a ReviewRetry row between the mistake
and the fix), so a wrong-then-right answer in normal practice earns nothing extra.
Coding exercises: a full pass fixes a failed exercise. An exercise first passed after
opening the solution only counts as fixed by a full pass after pressing Retry in Review
(which opens the starter code again), so copying the shown solution doesn't count.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.content.domains import LANGUAGES
from app.content.exercise_guides import explanation_for
from app.content.exercises import BY_SLUG as EXERCISES
from app.content.paths import PATHS, exercise_slugs
from app.models.models import (
    ExerciseAttempt,
    ExerciseHelp,
    Feedback,
    Question,
    QuizAnswer,
    QuizSession,
    Response,
    ReviewRetry,
    SkillDomain,
    User,
)

CONFIRM_DAYS = 3
FIX_XP = 5
SECOND_LOOK = 10  # fixes for the "Second Look" badge
LANGUAGE_NAMES = {lang["slug"]: lang["name"] for lang in LANGUAGES}
LEVELS = ("beginner", "intermediate", "advanced")
ANSWER_CHARS = 600
CODE_CHARS = 1500


def _aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _level(value) -> str:
    v = value.value if hasattr(value, "value") else str(value)
    return v if v in LEVELS else "intermediate"


def _topic_slug(topic: str) -> str:
    return "ex-" + re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")


@dataclass
class Item:
    kind: str  # question | exercise
    ref: int | str
    state: str = ""  # open | fixed | stuck
    reason: str = ""  # wrong | partial | timeout | failed | helped
    wrong_count: int = 0
    last_wrong_at: datetime | None = None
    opened_at: datetime | None = None  # exercises: when it went on the list (failing runs don't move it)
    fixed_at: datetime | None = None
    first_fix_at: datetime | None = None
    last_answer: str = ""
    last_feedback: str = ""
    last_score: float | None = None
    tests: tuple[int, int] | None = None

    @property
    def key(self) -> str:
        return f"q:{self.ref}" if self.kind == "question" else f"x:{self.ref}"

    def due_at(self) -> datetime | None:
        return self.fixed_at + timedelta(days=CONFIRM_DAYS) if self.state == "fixed" and self.fixed_at else None

    def status(self, now: datetime) -> str:
        """to_fix | check_again | waiting (fixed, not due yet) | done"""
        if self.state == "open":
            return "to_fix"
        if self.state == "fixed":
            return "check_again" if now >= self.due_at() else "waiting"
        return "done"


@dataclass
class History:
    items: dict[str, Item] = field(default_factory=dict)

    def fixes(self) -> list[tuple[Item, datetime]]:
        return sorted(((i, i.first_fix_at) for i in self.items.values() if i.first_fix_at), key=lambda t: t[1])


def short_feedback(fb: Feedback | None) -> str:
    """One or two plain sentences on what went wrong — never a line-by-line walkthrough."""
    if fb is None:
        return ""
    for m in fb.misconceptions or []:
        text = (m or {}).get("explanation") if isinstance(m, dict) else None
        if text:
            return str(text)[:300]
    missed = [str(x) for x in ((fb.details or {}).get("missed_concepts") or []) if x]
    if missed:
        return ("Missed: " + "; ".join(missed[:2]) + ".")[:300]
    raw = (fb.raw_explanation or "").strip()
    if raw:
        first = re.split(r"(?<=[.!?])\s", raw, maxsplit=1)[0]
        return first[:300]
    return ""


def key_idea(question: Question) -> str:
    """The question's general idea (its "Key idea" hint) without the answer itself."""
    for h in (question.rubric or {}).get("hints") or []:
        if h.startswith("Key idea:"):
            return h[len("Key idea:"):].strip()
    return ""


def hidden_response_ids(db: Session, user_id: int, now: datetime | None = None) -> set[int]:
    """Answers inside a running quiz that shows feedback only at the end: they don't count yet
    (no XP, no mistakes) so nothing gives the results away before the quiz is over."""
    from app.services.quiz import GRACE_S

    now = _aware(now)
    rows = (
        db.query(QuizAnswer.response_id, QuizSession.deadline_at)
        .join(QuizSession, QuizSession.id == QuizAnswer.quiz_id)
        .filter(QuizSession.user_id == user_id, QuizSession.status == "active", QuizSession.instant == 0,
                QuizAnswer.response_id.isnot(None))
        .all()
    )
    return {rid for rid, deadline in rows if _aware(deadline) + timedelta(seconds=GRACE_S) > now}


def build(db: Session, user: User, now: datetime | None = None) -> History:
    """Replay the learner's answers, quiz time-outs and exercise runs into review items."""
    now = _aware(now)
    hidden = hidden_response_ids(db, user.id, now)
    out = History()

    retries: dict[str, list[datetime]] = {}
    for r in db.query(ReviewRetry).filter(ReviewRetry.user_id == user.id).all():
        retries.setdefault(r.item, []).append(_aware(r.created_at))

    def retried_between(key: str, start: datetime | None, end: datetime) -> bool:
        return any((start is None or start <= t) and t <= end for t in retries.get(key, []))

    # ── Questions ──
    events: list[tuple[datetime, int, int, str, Response | None, Feedback | None]] = []
    rows = (
        db.query(Response, Feedback)
        .outerjoin(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id)
        .all()
    )
    for resp, fb in rows:
        if resp.id in hidden or fb is None:
            continue
        verdict = (fb.details or {}).get("verdict") or ""
        kind = "right" if verdict == "correct" else ("partial" if verdict.startswith("partial") else "wrong")
        events.append((_aware(resp.created_at), resp.id, resp.question_id, kind, resp, fb))
    # Questions left unanswered when a quiz ran out of time (or was ended) count as missed.
    unanswered = (
        db.query(QuizAnswer.question_id, QuizSession.finished_at, QuizAnswer.id)
        .join(QuizSession, QuizSession.id == QuizAnswer.quiz_id)
        .filter(QuizSession.user_id == user.id, QuizSession.status == "finished",
                QuizAnswer.response_id.is_(None))
        .all()
    )
    for qid, finished, aid in unanswered:
        events.append((_aware(finished), -aid, qid, "timeout", None, None))
    events.sort(key=lambda e: (e[0], e[1]))

    for when, _rid, qid, kind, resp, fb in events:
        key = f"q:{qid}"
        item = out.items.get(key)
        if kind == "right":
            if item is None:
                continue
            item.last_answer = (resp.answer_text or "")[:ANSWER_CHARS]
            item.last_score = fb.overall_score
            if item.state == "open":
                item.state, item.fixed_at = "fixed", when
                if not item.first_fix_at and retried_between(key, item.last_wrong_at, when):
                    item.first_fix_at = when
            elif item.state == "fixed" and when >= item.due_at():
                item.state = "stuck"
            continue
        if item is None:
            item = out.items[key] = Item("question", qid)
        item.state, item.reason, item.fixed_at = "open", kind, None
        item.wrong_count += 1
        item.last_wrong_at = when
        if resp is not None:
            item.last_answer = (resp.answer_text or "")[:ANSWER_CHARS]
            item.last_feedback = short_feedback(fb)
            item.last_score = fb.overall_score
        else:
            item.last_answer = ""
            item.last_feedback = "Time ran out before this one was answered."
            item.last_score = 0.0

    # ── Coding exercises ──
    attempts = (
        db.query(ExerciseAttempt)
        .filter(ExerciseAttempt.user_id == user.id)
        .order_by(ExerciseAttempt.created_at.asc(), ExerciseAttempt.id.asc())
        .all()
    )
    solution_at: dict[str, datetime] = {}
    for h in db.query(ExerciseHelp).filter(ExerciseHelp.user_id == user.id, ExerciseHelp.kind == "solution").all():
        if h.before_pass:
            t = _aware(h.created_at)
            solution_at[h.slug] = min(solution_at.get(h.slug, t), t)
    passed_once: set[str] = set()
    for a in attempts:
        e = EXERCISES.get(a.slug)
        if not e:
            continue
        when, total = _aware(a.created_at), len(e["tests"])
        full = a.passed >= total
        key = f"x:{a.slug}"
        item = out.items.get(key)
        if not full:
            # Failing runs while working are normal; they only open an item never passed yet.
            if a.slug not in passed_once:
                if item is None:
                    item = out.items[key] = Item("exercise", a.slug, state="open", reason="failed", opened_at=when)
                item.wrong_count += 1
                item.last_wrong_at = when
                item.last_answer = (a.code or "")[:CODE_CHARS]
                item.tests = (a.passed, total)
            continue
        first_pass = a.slug not in passed_once
        passed_once.add(a.slug)
        if first_pass and a.slug in solution_at and solution_at[a.slug] <= when:
            if item is None:
                item = out.items[key] = Item("exercise", a.slug)
            item.state, item.reason, item.last_wrong_at, item.opened_at = "open", "helped", when, when
            item.wrong_count = max(1, item.wrong_count)
            item.last_answer = (a.code or "")[:CODE_CHARS]
            item.tests = (a.passed, total)
            continue
        if item is None:
            continue
        if item.state == "open":
            via_review = retried_between(key, item.opened_at, when)
            if item.reason == "failed" or via_review:
                item.state, item.fixed_at = "fixed", when
                if not item.first_fix_at and via_review:
                    item.first_fix_at = when
                item.tests = (a.passed, total)
        elif item.state == "fixed" and when >= item.due_at() and retried_between(key, item.due_at(), when):
            item.state = "stuck"
    return out


# ----------------------------------------------------------------------------- XP

def awards(db: Session, user: User) -> tuple[dict[str, tuple[str, int, str, datetime]], dict[str, datetime]]:
    """+FIX_XP the first time each item is fixed (once per item, ever) and the Second Look badge."""
    hist = build(db, user)
    fixes = hist.fixes()
    if not fixes:
        return {}, {}
    titles = _titles(db, [i for i, _ in fixes])
    events = {
        f"fix:{item.key}": ("fix", FIX_XP, f"Fixed a mistake: {titles.get(item.key, 'an item')}"[:200], when)
        for item, when in fixes
    }
    badges = {"second-look": fixes[SECOND_LOOK - 1][1]} if len(fixes) >= SECOND_LOOK else {}
    return events, badges


def _titles(db: Session, items: list[Item]) -> dict[str, str]:
    qids = [i.ref for i in items if i.kind == "question"]
    out = {f"q:{qid}": title for qid, title in db.query(Question.id, Question.title).filter(Question.id.in_(qids)).all()} if qids else {}
    for i in items:
        if i.kind == "exercise" and i.ref in EXERCISES:
            out[i.key] = EXERCISES[i.ref]["title"]
    return out


# ----------------------------------------------------------------------------- the review page

def _path_sets(db: Session) -> dict[str, tuple[set[int], set[str]]]:
    from app.services import paths

    catalog = paths._catalog(db)
    out = {}
    for p in PATHS:
        qids: set[int] = set()
        slugs: set[str] = set()
        for s in p.steps:
            qids.update(paths.pool_ids(s, catalog))
            slugs.update(exercise_slugs(s.exercise))
        out[p.slug] = (qids, slugs)
    return out


REASONS = {
    "wrong": "Wrong answer",
    "partial": "Partly right",
    "timeout": "Not answered in time",
    "failed": "Tests failing",
    "helped": "Solved with help",
}


def page(db: Session, user: User, *, topic: str = "", language: str = "", path: str = "",
         difficulty: str = "", kind: str = "", now: datetime | None = None) -> dict:
    now = _aware(now)
    hist = build(db, user, now)
    items = list(hist.items.values())
    qids = [i.ref for i in items if i.kind == "question"]
    questions = {
        q.id: (q, d)
        for q, d in db.query(Question, SkillDomain).join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Question.id.in_(qids)).all()
    } if qids else {}
    path_sets = _path_sets(db)

    cards = []
    for it in items:
        status = it.status(now)
        if it.kind == "question":
            if it.ref not in questions:
                continue
            q, d = questions[it.ref]
            meta = {
                "kind": "question", "id": q.id, "slug": None, "title": q.title, "language": q.language,
                "topic": d.slug, "topic_name": d.name, "difficulty": _level(q.difficulty),
                "question_kind": (q.rubric or {}).get("kind") or "explain",
                "explanation": key_idea(q), "code": q.code or "",
            }
            in_path = [p for p, (ids, _) in path_sets.items() if q.id in ids]
        else:
            e = EXERCISES.get(it.ref)
            if not e:
                continue
            guide = explanation_for(e["slug"], e["language"]) or {}
            meta = {
                "kind": "exercise", "id": None, "slug": e["slug"], "title": e["title"], "language": e["language"],
                "topic": _topic_slug(e["topic"]), "topic_name": e["topic"], "difficulty": _level(e["difficulty"]),
                "question_kind": "code", "explanation": guide.get("idea", ""), "code": "",
            }
            in_path = [p for p, (_, slugs) in path_sets.items() if e["slug"] in slugs]
        due = it.due_at()
        cards.append({
            **meta,
            "key": it.key,
            "status": status,
            "reason": it.reason,
            "reason_label": REASONS.get(it.reason, "Mistake"),
            "times_wrong": it.wrong_count,
            "last_wrong_at": it.last_wrong_at,
            "fixed_at": it.fixed_at,
            "due_at": due,
            "last_answer": it.last_answer,
            "feedback": it.last_feedback if it.kind == "question" else (
                f"{it.tests[0]} of {it.tests[1]} tests passed." if it.reason == "failed" and it.tests else
                "Passed after opening the solution. Solve it again from scratch." if it.reason == "helped" else ""),
            "score": it.last_score,
            "tests": list(it.tests) if it.tests else None,
            "paths": in_path,
        })

    # Filter options come from everything on the learner's list (before filtering).
    listed = [c for c in cards if c["status"] in ("to_fix", "check_again")]

    def opts(field_: str, name_of) -> list[dict]:
        seen: dict[str, int] = {}
        for c in listed:
            for v in (c[field_] if isinstance(c[field_], list) else [c[field_]]):
                seen[v] = seen.get(v, 0) + 1
        return [{"value": v, "label": name_of(v), "count": n} for v, n in sorted(seen.items(), key=lambda t: name_of(t[0]))]

    topic_names = {c["topic"]: c["topic_name"] for c in cards}
    path_names = {p.slug: p.name for p in PATHS}
    filters = {
        "topics": opts("topic", lambda v: topic_names.get(v, v)),
        "languages": opts("language", lambda v: LANGUAGE_NAMES.get(v, v)),
        "paths": opts("paths", lambda v: path_names.get(v, v)),
        "difficulties": sorted(opts("difficulty", lambda v: v.capitalize()), key=lambda o: LEVELS.index(o["value"])),
    }

    def keep(c: dict) -> bool:
        return ((not topic or c["topic"] == topic) and (not language or c["language"] == language)
                and (not path or path in c["paths"]) and (not difficulty or c["difficulty"] == difficulty)
                and (not kind or c["kind"] == kind))

    shown = [c for c in listed if keep(c)]
    shown.sort(key=lambda c: (c["status"] != "check_again", -_aware(c["last_wrong_at"] or c["fixed_at"]).timestamp()))
    waiting = sorted((c for c in cards if c["status"] == "waiting"), key=lambda c: c["due_at"])
    fixes = len(hist.fixes())
    return {
        "items": shown,
        "coming_back": [{"key": c["key"], "title": c["title"], "fixed_at": c["fixed_at"], "due_at": c["due_at"]}
                        for c in waiting[:8]],
        "counts": {
            "to_fix": sum(c["status"] == "to_fix" for c in listed),
            "check_again": sum(c["status"] == "check_again" for c in listed),
            "waiting": len(waiting),
            "done": sum(c["status"] == "done" for c in cards),
            "shown": len(shown),
        },
        "fixes": fixes,
        "filters": filters,
        "rules": {"fix_xp": FIX_XP, "confirm_days": CONFIRM_DAYS, "second_look": SECOND_LOOK},
    }


def mark_retry(db: Session, user: User, key: str) -> None:
    """Remember that the learner is retrying this item from Review (see the module notes)."""
    db.add(ReviewRetry(user_id=user.id, item=key))
    db.commit()
