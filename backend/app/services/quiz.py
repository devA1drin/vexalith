"""Timed quizzes: a fixed set of questions against a clock kept on the server.

The start time and deadline are stored with the quiz, so a page refresh (or another device)
sees the same remaining time. Answers are saved before grading, so a slow grader never loses
one. Answers arriving more than GRACE_S after the deadline are refused, and a quiz past its
deadline is finished on the next request (anything typed is graded, the rest is unanswered).

Grading uses the normal grader (English, Filipino and Taglish). Missed and unanswered
questions show up in mistake review. XP: the usual answer XP, plus QUIZ_XP for each question
whose first correct answer ever was given in a quiz, so repeating questions earns nothing.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.content.domains import LANGUAGES
from app.content.paths import BY_SLUG as PATHS_BY_SLUG
from app.content.paths import PATHS
from app.models.models import (
    Feedback,
    Question,
    QuizAnswer,
    QuizSession,
    Response,
    SkillDomain,
    SkillMastery,
    User,
    XpEvent,
)
from app.services import adaptive
from app.services.review import key_idea, short_feedback

logger = logging.getLogger(__name__)

LENGTHS = (5, 10, 20)
MINUTES = (5, 10, 15)
GRACE_S = 15
MIN_POOL = 5
QUIZ_XP = 3
BEAT_SCORE = 0.8
BEAT_MIN = 10
SCOPES = ("topic", "language", "path", "mixed")
LEVELS = ("beginner", "intermediate", "advanced")
LANGUAGE_NAMES = {lang["slug"]: lang["name"] for lang in LANGUAGES}


class QuizError(Exception):
    def __init__(self, status: int, detail: str, quiz_id: int | None = None):
        super().__init__(detail)
        self.status, self.detail, self.quiz_id = status, detail, quiz_id


def _aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _level(value) -> str:
    v = value.value if hasattr(value, "value") else str(value)
    return v if v in LEVELS else "intermediate"


def _kind(q: Question) -> str:
    return (q.rubric or {}).get("kind") or "explain"


# ----------------------------------------------------------------------------- what can be quizzed

def _pool(db: Session, scope: str, value: str) -> list[tuple[Question, SkillDomain]]:
    query = (
        db.query(Question, SkillDomain)
        .join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Question.source == "seed")
    )
    if scope == "topic":
        query = query.filter(SkillDomain.slug == value)
    elif scope == "language":
        query = query.filter(Question.language == value)
    elif scope == "path":
        from app.services import paths

        p = PATHS_BY_SLUG.get(value)
        if p is None:
            return []
        catalog = paths._catalog(db)
        ids = {qid for s in p.steps for qid in paths.pool_ids(s, catalog)}
        query = query.filter(Question.id.in_(ids))
    return query.all()


def scope_label(db: Session, scope: str, value: str) -> str:
    if scope == "topic":
        d = db.query(SkillDomain).filter_by(slug=value).first()
        return d.name if d else value
    if scope == "language":
        return LANGUAGE_NAMES.get(value, value)
    if scope == "path":
        p = PATHS_BY_SLUG.get(value)
        return f"{p.name} path" if p else value
    return "Everything"


def options(db: Session, user: User, now: datetime | None = None) -> dict:
    rows = (
        db.query(Question.id, Question.language, SkillDomain.slug, SkillDomain.name)
        .join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Question.source == "seed")
        .all()
    )
    topics: dict[str, list] = {}
    langs: dict[str, int] = {}
    for _qid, lang, slug, name in rows:
        topics.setdefault(slug, [name, 0])[1] += 1
        langs[lang] = langs.get(lang, 0) + 1
    from app.services import paths

    catalog = paths._catalog(db)
    path_opts = []
    for p in PATHS:
        n = len({qid for s in p.steps for qid in paths.pool_ids(s, catalog)})
        if n >= MIN_POOL:
            path_opts.append({"value": p.slug, "label": p.name, "count": n})
    active = active_quiz(db, user, now)
    return {
        "scopes": {
            "topic": [{"value": s, "label": n, "count": c} for s, (n, c) in topics.items() if c >= MIN_POOL],
            "language": [{"value": lang["slug"], "label": lang["name"], "count": langs.get(lang["slug"], 0)}
                         for lang in LANGUAGES if langs.get(lang["slug"], 0) >= MIN_POOL],
            "path": path_opts,
            "mixed": [{"value": "", "label": "Everything", "count": len(rows)}],
        },
        "lengths": list(LENGTHS),
        "minutes": list(MINUTES),
        "active": _brief(active, now) if active else None,
        "rules": rules(),
    }


def rules() -> dict:
    return {"quiz_xp": QUIZ_XP, "grace_s": GRACE_S, "beat_score": BEAT_SCORE, "beat_min": BEAT_MIN}


# ----------------------------------------------------------------------------- picking questions

def _is_short(q: Question) -> bool:
    lines = len([ln for ln in (q.code or "").splitlines() if ln.strip()])
    return lines <= 8 and len(q.prompt or "") <= 320


def pick(db: Session, user: User, pool: list[tuple[Question, SkillDomain]], n: int,
         rng: random.Random | None = None) -> list[int]:
    """Short questions first (fill-in, then short snippets), ones not answered right yet,
    near the learner's level, avoiding the last few quizzes; then ordered easy to hard."""
    rng = rng or random.Random()
    right: set[int] = set()
    for qid, details in (
        db.query(Response.question_id, Feedback.details)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id).all()
    ):
        if (details or {}).get("verdict") == "correct":
            right.add(qid)
    recent: set[int] = set()
    for (ids,) in (db.query(QuizSession.question_ids).filter(QuizSession.user_id == user.id)
                   .order_by(QuizSession.id.desc()).limit(3).all()):
        recent.update(ids or [])
    mastery = {m.domain_id: m.mastery for m in db.query(SkillMastery).filter_by(user_id=user.id).all()}

    def score(q: Question) -> float:
        s = 3.0 if _kind(q) == "fill_blank" else (2.0 if _is_short(q) else 0.0)
        s += 3.0 if q.id not in right else 0.0
        s -= 4.0 if q.id in recent else 0.0
        target = adaptive.mastery_to_difficulty(mastery.get(q.domain_id, 0.5))
        gap = abs(LEVELS.index(_level(q.difficulty)) - LEVELS.index(target if target in LEVELS else "intermediate"))
        s += (1.5, 0.5, 0.0)[gap]
        return s + rng.random() * 2

    chosen = sorted((q for q, _ in pool), key=score, reverse=True)[:n]
    chosen.sort(key=lambda q: (LEVELS.index(_level(q.difficulty)), rng.random()))
    return [q.id for q in chosen]


# ----------------------------------------------------------------------------- lifecycle

def active_quiz(db: Session, user: User, now: datetime | None = None) -> QuizSession | None:
    """The learner's running quiz, if any (one past its deadline is finished first)."""
    now = _aware(now)
    found = None
    for quiz in db.query(QuizSession).filter_by(user_id=user.id, status="active").all():
        if now > _aware(quiz.deadline_at) + timedelta(seconds=GRACE_S):
            finish(db, user, quiz, now=now, ended_by="time")
        else:
            found = quiz
    return found


def close_expired(db: Session, user: User, now: datetime | None = None) -> None:
    active_quiz(db, user, now)


def start(db: Session, user: User, *, scope: str, value: str, length: int, minutes: int, instant: bool,
          now: datetime | None = None, rng: random.Random | None = None) -> QuizSession:
    now = _aware(now)
    if scope not in SCOPES:
        raise QuizError(422, "Pick a topic, language, path or everything")
    if length not in LENGTHS:
        raise QuizError(422, f"Length must be one of {', '.join(map(str, LENGTHS))}")
    if minutes not in MINUTES:
        raise QuizError(422, f"Time limit must be one of {', '.join(map(str, MINUTES))} minutes")
    running = active_quiz(db, user, now)
    if running is not None:
        raise QuizError(409, "You already have a quiz running", running.id)
    value = "" if scope == "mixed" else value
    pool = _pool(db, scope, value)
    if len(pool) < MIN_POOL:
        raise QuizError(404, "Not enough questions for that choice")
    ids = pick(db, user, pool, min(length, len(pool)), rng)
    quiz = QuizSession(
        user_id=user.id, scope=scope, scope_value=value, scope_label=scope_label(db, scope, value)[:120],
        length=len(ids), time_limit_s=minutes * 60, instant=1 if instant else 0, question_ids=ids,
        status="active", started_at=now, deadline_at=now + timedelta(minutes=minutes),
    )
    db.add(quiz)
    db.flush()
    db.add_all(QuizAnswer(quiz_id=quiz.id, user_id=user.id, position=i, question_id=qid) for i, qid in enumerate(ids))
    db.commit()
    db.refresh(quiz)
    return quiz


def get(db: Session, user: User, quiz_id: int, now: datetime | None = None) -> QuizSession:
    quiz = db.get(QuizSession, quiz_id)
    if quiz is None or quiz.user_id != user.id:
        raise QuizError(404, "Quiz not found")
    if quiz.status == "active" and _aware(now) > _aware(quiz.deadline_at) + timedelta(seconds=GRACE_S):
        finish(db, user, quiz, now=now, ended_by="time")
    return quiz


def _slots(db: Session, quiz: QuizSession) -> list[QuizAnswer]:
    return db.query(QuizAnswer).filter_by(quiz_id=quiz.id).order_by(QuizAnswer.position.asc()).all()


def _verdicts(db: Session, slots: list[QuizAnswer]) -> dict[int, Feedback]:
    rids = [s.response_id for s in slots if s.response_id]
    if not rids:
        return {}
    return {fb.response_id: fb for fb in db.query(Feedback).filter(Feedback.response_id.in_(rids)).all()}


def _grade(db: Session, user: User, slot: QuizAnswer) -> None:
    from app.services.learning import submit_response

    question = db.get(Question, slot.question_id)
    if question is None or not slot.answer_text.strip():
        return
    response, _payload = submit_response(db, user=user, question=question, answer_text=slot.answer_text)
    slot.response_id = response.id
    db.commit()


def answer(db: Session, user: User, quiz_id: int, position: int, text: str, now: datetime | None = None) -> dict:
    """Save, then grade, one answer. Returns the quiz state (and feedback in instant mode)."""
    now = _aware(now)
    quiz = get(db, user, quiz_id, now)
    if quiz.status != "active":
        raise QuizError(409, "This quiz is over")
    slot = db.query(QuizAnswer).filter_by(quiz_id=quiz.id, position=position).first()
    if slot is None:
        raise QuizError(404, "No such question in this quiz")
    if slot.response_id is not None or slot.answer_text:
        raise QuizError(409, "Already answered")
    text = (text or "").strip()
    if not text:
        raise QuizError(422, "Write an answer, or skip this one")
    slot.answer_text, slot.skipped, slot.answered_at = text[:4000], 0, now
    db.commit()  # saved first: a grader hiccup never loses the answer
    feedback = None
    try:
        from app.services.learning import submit_response

        question = db.get(Question, slot.question_id)
        response, payload = submit_response(db, user=user, question=question, answer_text=slot.answer_text, now=now)
        slot.response_id = response.id
        db.commit()
        feedback = payload
    except Exception:  # noqa: BLE001 — finish() grades it again
        db.rollback()
        logger.exception("Quiz %s answer %s couldn't be graded yet", quiz.id, position)
    if all(s.response_id or s.answer_text for s in _slots(db, quiz)):
        finish(db, user, quiz, now=now, ended_by="done")
    elif quiz.instant:
        from app.services.xp import safe_sync

        safe_sync(db, user)
    out = state(db, user, quiz, now)
    out["feedback"] = feedback.model_dump(mode="json") if (feedback is not None and quiz.instant) else None
    return out


def skip(db: Session, user: User, quiz_id: int, position: int, now: datetime | None = None) -> dict:
    now = _aware(now)
    quiz = get(db, user, quiz_id, now)
    if quiz.status != "active":
        raise QuizError(409, "This quiz is over")
    slot = db.query(QuizAnswer).filter_by(quiz_id=quiz.id, position=position).first()
    if slot is None:
        raise QuizError(404, "No such question in this quiz")
    if not slot.answer_text:
        slot.skipped = 1
        db.commit()
    return state(db, user, quiz, now)


def finish(db: Session, user: User, quiz: QuizSession, *, now: datetime | None = None, ended_by: str = "ended") -> QuizSession:
    """End the quiz: grade anything saved but not graded, count the score, award XP."""
    now = _aware(now)
    if quiz.status == "finished":
        return quiz
    slots = _slots(db, quiz)
    for slot in slots:
        if slot.answer_text and slot.response_id is None:
            try:
                _grade(db, user, slot)
            except Exception:  # noqa: BLE001
                db.rollback()
                logger.exception("Quiz %s: couldn't grade position %s", quiz.id, slot.position)
    fbs = _verdicts(db, slots)
    correct = sum(1 for s in slots if s.response_id in fbs and (fbs[s.response_id].details or {}).get("verdict") == "correct")
    deadline = _aware(quiz.deadline_at)
    quiz.correct = correct
    quiz.score = round(correct / quiz.length, 4) if quiz.length else 0.0
    quiz.finished_at = min(now, deadline)
    quiz.ended_by = "time" if now >= deadline and ended_by != "done" else ended_by
    quiz.status = "finished"
    db.commit()
    from app.services.xp import safe_sync

    safe_sync(db, user)
    return quiz


# ----------------------------------------------------------------------------- read models

def _brief(quiz: QuizSession, now: datetime | None = None) -> dict:
    now = _aware(now)
    return {
        "id": quiz.id, "scope": quiz.scope, "scope_value": quiz.scope_value, "scope_label": quiz.scope_label,
        "length": quiz.length, "time_limit_s": quiz.time_limit_s, "instant": bool(quiz.instant),
        "status": quiz.status, "started_at": _aware(quiz.started_at), "deadline_at": _aware(quiz.deadline_at),
        "remaining_s": max(0.0, round((_aware(quiz.deadline_at) - now).total_seconds(), 1)),
    }


def state(db: Session, user: User, quiz: QuizSession, now: datetime | None = None) -> dict:
    from app.services.learning import _question_out

    now = _aware(now)
    slots = _slots(db, quiz)
    fbs = _verdicts(db, slots) if quiz.instant else {}
    current = next((s for s in slots if not s.answer_text and not s.skipped), None)
    returning = False
    if current is None:
        current = next((s for s in slots if not s.answer_text), None)
        returning = current is not None
    question = None
    questions: list[dict] = []
    if quiz.status == "active":
        # Every question comes with the state, so the page can move on without waiting for grading.
        rows = {
            q.id: (q, d) for q, d in db.query(Question, SkillDomain).join(SkillDomain, SkillDomain.id == Question.domain_id)
            .filter(Question.id.in_([s.question_id for s in slots])).all()
        }
        questions = [_question_out(*rows[s.question_id]).model_dump(mode="json") if s.question_id in rows else None for s in slots]
        if current is not None:
            question = questions[current.position]
    out = _brief(quiz, now)
    out.update({
        "server_now": now,
        "current": current.position if (current is not None and quiz.status == "active") else None,
        "returning": returning,
        "question": question,
        "questions": questions,
        "slots": [
            {
                "position": s.position,
                "state": "answered" if s.answer_text else ("skipped" if s.skipped else "open"),
                "verdict": ((fbs[s.response_id].details or {}).get("verdict") if s.response_id in fbs else None),
            }
            for s in slots
        ],
        "answered": sum(1 for s in slots if s.answer_text),
    })
    return out


def _quiz_xp(db: Session, user: User, slots: list[QuizAnswer]) -> int:
    rids = [s.response_id for s in slots if s.response_id]
    if not rids:
        return 0
    made = {r.id: (r.question_id, _aware(r.created_at)) for r in db.query(Response).filter(Response.id.in_(rids)).all()}
    keys = {}
    for qid, when in made.values():
        for k in (f"answer:{qid}", f"quizq:{qid}", f"fix:q:{qid}"):
            keys[k] = when
    total = 0
    for ev in db.query(XpEvent).filter(XpEvent.user_id == user.id, XpEvent.key.in_(list(keys))).all():
        if abs((_aware(ev.created_at) - keys[ev.key]).total_seconds()) < 0.001:
            total += ev.amount
    return total


def results(db: Session, user: User, quiz_id: int, now: datetime | None = None) -> dict:
    quiz = get(db, user, quiz_id, now)
    if quiz.status != "finished":
        raise QuizError(409, "This quiz is still running")
    slots = _slots(db, quiz)
    fbs = _verdicts(db, slots)
    questions = {
        q.id: (q, d) for q, d in db.query(Question, SkillDomain).join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Question.id.in_([s.question_id for s in slots])).all()
    }
    review = []
    for s in slots:
        q, d = questions[s.question_id]
        fb = fbs.get(s.response_id)
        verdict = (fb.details or {}).get("verdict") if fb else None
        status = ("correct" if verdict == "correct" else "partial" if (verdict or "").startswith("partial")
                  else "wrong" if fb else ("skipped" if s.skipped else "unanswered"))
        rubric = q.rubric or {}
        review.append({
            "position": s.position, "question_id": q.id, "title": q.title, "language": q.language,
            "difficulty": _level(q.difficulty), "topic_name": d.name, "kind": _kind(q),
            "code": q.code or "", "prompt": q.prompt, "answer": s.answer_text, "status": status,
            "score": fb.overall_score if fb else 0.0,
            "feedback": short_feedback(fb) if fb and status != "correct" else "",
            "reference_answer": rubric.get("reference_answer") or "",
            "accepted_answers": list(rubric.get("accepted_answers") or [])[:3] if _kind(q) == "fill_blank" else [],
            "key_idea": key_idea(q),
        })
    prior = (
        db.query(QuizSession)
        .filter(QuizSession.user_id == user.id, QuizSession.status == "finished", QuizSession.id != quiz.id,
                QuizSession.scope == quiz.scope, QuizSession.scope_value == quiz.scope_value)
        .all()
    )
    prior = [p for p in prior if _aware(p.finished_at) <= _aware(quiz.finished_at)]
    best_before = max((p.score for p in prior), default=None)
    used = (_aware(quiz.finished_at) - _aware(quiz.started_at)).total_seconds()
    return {
        **_brief(quiz),
        "remaining_s": 0.0,
        "finished_at": _aware(quiz.finished_at),
        "ended_by": quiz.ended_by,
        "correct": quiz.correct,
        "score": quiz.score,
        "time_used_s": int(max(0, min(used, quiz.time_limit_s))),
        "xp": _quiz_xp(db, user, slots),
        "to_review": sum(1 for r in review if r["status"] != "correct"),
        "best_before": best_before,
        "new_best": best_before is None or quiz.score > best_before,
        "beat_the_clock": quiz.length >= BEAT_MIN and quiz.score >= BEAT_SCORE,
        "questions": review,
    }


def history(db: Session, user: User, now: datetime | None = None) -> dict:
    close_expired(db, user, now)
    done = (
        db.query(QuizSession)
        .filter(QuizSession.user_id == user.id, QuizSession.status == "finished")
        .order_by(QuizSession.finished_at.desc(), QuizSession.id.desc())
        .all()
    )
    best: dict[tuple[str, str], dict] = {}
    for q in done:
        b = best.setdefault((q.scope, q.scope_value), {
            "scope": q.scope, "scope_value": q.scope_value, "scope_label": q.scope_label,
            "best_score": q.score, "best_correct": q.correct, "best_length": q.length, "attempts": 0,
            "last_at": _aware(q.finished_at),
        })
        b["attempts"] += 1
        if q.score > b["best_score"]:
            b.update(best_score=q.score, best_correct=q.correct, best_length=q.length)
    return {
        "quizzes": [
            {
                "id": q.id, "scope": q.scope, "scope_value": q.scope_value, "scope_label": q.scope_label,
                "length": q.length, "correct": q.correct, "score": q.score, "instant": bool(q.instant),
                "time_limit_s": q.time_limit_s, "ended_by": q.ended_by, "finished_at": _aware(q.finished_at),
                "time_used_s": int(max(0, min((_aware(q.finished_at) - _aware(q.started_at)).total_seconds(), q.time_limit_s))),
            }
            for q in done[:30]
        ],
        "best": sorted(best.values(), key=lambda b: (-b["attempts"], b["scope_label"])),
        "total": len(done),
    }


# ----------------------------------------------------------------------------- XP

def awards(db: Session, user: User, first_correct: dict[int, tuple[int, datetime, str]]) -> tuple[dict, dict]:
    """QUIZ_XP for questions first answered right inside a quiz; Beat the Clock badge."""
    events: dict[str, tuple[str, int, str, datetime]] = {}
    quiz_rids = {
        rid for (rid,) in db.query(QuizAnswer.response_id)
        .filter(QuizAnswer.user_id == user.id, QuizAnswer.response_id.isnot(None)).all()
    }
    for qid, (rid, when, title) in first_correct.items():
        if rid in quiz_rids:
            events[f"quizq:{qid}"] = ("quiz", QUIZ_XP, f"Quiz bonus: {title}"[:200], when)
    badges: dict[str, datetime] = {}
    beat = (
        db.query(QuizSession.finished_at)
        .filter(QuizSession.user_id == user.id, QuizSession.status == "finished",
                QuizSession.length >= BEAT_MIN, QuizSession.score >= BEAT_SCORE)
        .order_by(QuizSession.finished_at.asc())
        .first()
    )
    if beat:
        badges["beat-the-clock"] = _aware(beat[0])
    return events, badges
