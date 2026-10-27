"""Bookmarks: questions ("q:<id>") and coding exercises ("x:<slug>") a learner saved, each with
an optional short note. The list carries what the Bookmarks page needs to filter and practise."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content.domains import LANGUAGES
from app.content.exercises import BY_SLUG as EXERCISES
from app.models.models import Bookmark, ExerciseAttempt, Feedback, Question, Response, SkillDomain, User
from app.services import review

NOTE_MAX = 140
MAX_BOOKMARKS = 500
LANGUAGE_NAMES = {lang["slug"]: lang["name"] for lang in LANGUAGES}
_CONTROL = re.compile(r"[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")


class BookmarkError(ValueError):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def clean_note(value: str | None) -> str:
    v = unicodedata.normalize("NFKC", value or "")
    v = re.sub(r"\s+", " ", _CONTROL.sub(" ", v)).strip()
    if len(v) > NOTE_MAX:
        raise BookmarkError(422, f"Keep the note to {NOTE_MAX} characters.")
    return v


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def keys(db: Session, user: User) -> list[str]:
    return [k for (k,) in db.query(Bookmark.item).filter(Bookmark.user_id == user.id).all()]


def set_saved(db: Session, user: User, key: str, saved: bool, note: str | None = None) -> dict:
    """Save (or update the note of) an item, or remove it. Idempotent."""
    row = db.query(Bookmark).filter(Bookmark.user_id == user.id, Bookmark.item == key).one_or_none()
    if not saved:
        if row is not None:
            db.delete(row)
            db.commit()
        return {"key": key, "saved": False, "note": ""}
    clean = clean_note(note) if note is not None else None
    if row is None:
        if db.query(Bookmark.id).filter(Bookmark.user_id == user.id).count() >= MAX_BOOKMARKS:
            raise BookmarkError(409, f"You can keep up to {MAX_BOOKMARKS} bookmarks. Remove some first.")
        row = Bookmark(user_id=user.id, item=key, note=clean or "")
        db.add(row)
        try:
            db.commit()
        except IntegrityError:  # saved twice at once: keep the one that won
            db.rollback()
            row = db.query(Bookmark).filter(Bookmark.user_id == user.id, Bookmark.item == key).one()
    elif clean is not None and clean != row.note:
        row.note = clean
        db.commit()
    return {"key": key, "saved": True, "note": row.note}


def _question_results(db: Session, user: User, qids: list[int]) -> dict[int, str]:
    """The latest verdict per question: right | partial | wrong (answers hidden in a running quiz don't count)."""
    if not qids:
        return {}
    hidden = review.hidden_response_ids(db, user.id)
    rows = (
        db.query(Response.id, Response.question_id, Feedback.details)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id, Response.question_id.in_(qids))
        .order_by(Response.created_at.asc(), Response.id.asc())
        .all()
    )
    out: dict[int, str] = {}
    for rid, qid, details in rows:
        if rid in hidden:
            continue
        verdict = (details or {}).get("verdict") or ""
        out[qid] = "right" if verdict == "correct" else "partial" if verdict.startswith("partial") else "wrong"
    return out


def _exercise_results(db: Session, user: User, slugs: list[str]) -> dict[str, str]:
    if not slugs:
        return {}
    out: dict[str, str] = {}
    for slug, passed, total in db.query(ExerciseAttempt.slug, ExerciseAttempt.passed, ExerciseAttempt.total).filter(
        ExerciseAttempt.user_id == user.id, ExerciseAttempt.slug.in_(slugs)
    ).all():
        if total and passed >= total:
            out[slug] = "solved"
        else:
            out.setdefault(slug, "failed")
    return out


def page(db: Session, user: User, *, kind: str = "", topic: str = "", language: str = "") -> dict:
    rows = db.query(Bookmark).filter(Bookmark.user_id == user.id).order_by(Bookmark.created_at.desc(), Bookmark.id.desc()).all()
    qids = [int(r.item[2:]) for r in rows if r.item.startswith("q:") and r.item[2:].isdigit()]
    slugs = [r.item[2:] for r in rows if r.item.startswith("x:")]
    questions = {
        q.id: (q, d)
        for q, d in db.query(Question, SkillDomain).join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Question.id.in_(qids)).all()
    } if qids else {}
    q_results = _question_results(db, user, qids)
    x_results = _exercise_results(db, user, slugs)

    cards = []
    for r in rows:
        base = {"key": r.item, "note": r.note, "saved_at": _aware(r.created_at)}
        if r.item.startswith("q:"):
            qid = int(r.item[2:]) if r.item[2:].isdigit() else -1
            if qid not in questions:
                continue
            q, d = questions[qid]
            cards.append({
                **base, "kind": "question", "id": q.id, "slug": None, "title": q.title, "language": q.language,
                "topic": d.slug, "topic_name": d.name, "difficulty": review._level(q.difficulty),
                "question_kind": (q.rubric or {}).get("kind") or "explain",
                "result": q_results.get(q.id, "new"),
            })
        else:
            e = EXERCISES.get(r.item[2:])
            if not e:
                continue
            cards.append({
                **base, "kind": "exercise", "id": None, "slug": e["slug"], "title": e["title"], "language": e["language"],
                "topic": review._topic_slug(e["topic"]), "topic_name": e["topic"], "difficulty": review._level(e["difficulty"]),
                "question_kind": "code", "result": x_results.get(e["slug"], "new"),
            })

    def opts(field_: str, names: dict[str, str]) -> list[dict]:
        seen: dict[str, int] = {}
        for c in cards:
            seen[c[field_]] = seen.get(c[field_], 0) + 1
        return [{"value": v, "label": names.get(v, v), "count": n} for v, n in sorted(seen.items(), key=lambda t: names.get(t[0], t[0]))]

    shown = [
        c for c in cards
        if (not kind or c["kind"] == kind) and (not topic or c["topic"] == topic) and (not language or c["language"] == language)
    ]
    return {
        "items": shown,
        "counts": {
            "total": len(cards),
            "questions": sum(c["kind"] == "question" for c in cards),
            "exercises": sum(c["kind"] == "exercise" for c in cards),
            "shown": len(shown),
        },
        "filters": {
            "topics": opts("topic", {c["topic"]: c["topic_name"] for c in cards}),
            "languages": opts("language", LANGUAGE_NAMES),
        },
        "limits": {"note": NOTE_MAX, "max": MAX_BOOKMARKS},
    }
