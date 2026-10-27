"""Admin dashboard: who is an admin, the audit log, and the read models behind each page.

Admin access is decided by sign-in identity ("provider:account_id", the same form the
maintenance purge uses) listed in ADMIN_IDENTITIES. Emails are never used to decide access.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import get_settings
from app.content.exercises import BY_SLUG
from app.models.models import (
    AdminAudit, ExerciseAttempt, Feedback, FeedbackModeration, LearnerFlag, LearnerProfile, Question,
    QuestionEdit, Response, SkillDomain, User, UserFeedback, UserSettings, XpEvent,
)
from app.services.daily import MANILA
from app.services.question_edits import key_idea_of, split_prompt
from app.services.xp import level_for, level_name, public_name

LANGUAGE_LABELS = {
    "python": "Python", "javascript": "JavaScript", "cpp": "C++", "php": "PHP", "java": "Java",
    "html": "HTML", "css": "CSS", "general": "Logic & prose",
}
DIFFICULTY_START = {"beginner": 0.25, "intermediate": 0.55, "advanced": 0.85}
VERDICT_SCORE = {"correct": 1.0, "partially_correct": 0.5, "incorrect": 0.0}
HARDEST_MIN_ATTEMPTS = 3


def identity(user: User) -> str:
    return f"{user.auth_provider}:{user.provider_account_id}".lower()


def is_admin(user: User | None) -> bool:
    return user is not None and identity(user) in get_settings().admin_identity_set


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def _enum(v) -> str:
    return getattr(v, "value", v) or ""


# ----------------------------------------------------------------------------- audit

def audit(db: Session, actor: User, action: str, target: str, **details) -> None:
    db.add(AdminAudit(actor_id=actor.id, actor_name=actor.display_name[:80], action=action,
                      target=target[:120], details=details))


def audit_page(db: Session, *, action: str = "", page: int = 1, size: int = 30) -> dict:
    q = db.query(AdminAudit)
    if action:
        q = q.filter(AdminAudit.action == action)
    total = q.count()
    rows = q.order_by(AdminAudit.created_at.desc(), AdminAudit.id.desc()).offset((page - 1) * size).limit(size).all()
    actions = [a for (a,) in db.query(AdminAudit.action).distinct().order_by(AdminAudit.action)]
    return {
        "items": [{"id": r.id, "actor": r.actor_name, "action": r.action, "target": r.target,
                   "details": r.details or {}, "created_at": _aware(r.created_at)} for r in rows],
        "total": total, "page": page, "pages": max(1, math.ceil(total / size)), "actions": actions,
    }


# ----------------------------------------------------------------------------- answers (shared)

def _answers(db: Session) -> list[tuple[int, int, int, datetime, str, float]]:
    """(response id, user id, question id, time, verdict, score) for every graded answer, oldest first."""
    rows = (
        db.query(Response.id, Response.user_id, Response.question_id, Response.created_at, Feedback.details, Feedback.overall_score)
        .join(Feedback, Feedback.response_id == Response.id)
        .order_by(Response.created_at, Response.id)
        .all()
    )
    out = []
    for rid, uid, qid, at, details, score in rows:
        verdict = (details or {}).get("verdict") or ("correct" if (score or 0) >= 0.75 else "partially_correct" if (score or 0) >= 0.4 else "incorrect")
        out.append((rid, uid, qid, _aware(at), verdict, float(score or 0)))
    return out


def question_stats(db: Session, answers=None) -> dict[int, dict]:
    """Per question: attempts, learners, verdict counts and an Elo-style difficulty rating.

    The rating replays every answer in order. Each question starts at its labelled
    difficulty, each learner at 0.5; a miss on a question the learner was expected to get
    pushes the question's rating up, a solve pushes it down. Shown on a 0-1000 scale.
    """
    answers = _answers(db) if answers is None else answers
    diff = {qid: _enum(d) for qid, d in db.query(Question.id, Question.difficulty)}
    rating = {qid: DIFFICULTY_START.get(d, 0.55) for qid, d in diff.items()}
    ability: dict[int, float] = defaultdict(lambda: 0.5)
    stats: dict[int, dict] = {}
    k = 0.08
    for _rid, uid, qid, _at, verdict, score in answers:
        s = stats.setdefault(qid, {"attempts": 0, "learners": set(), "correct": 0, "partially_correct": 0, "incorrect": 0})
        s["attempts"] += 1
        s["learners"].add(uid)
        s[verdict if verdict in VERDICT_SCORE else "incorrect"] += 1
        r = rating.get(qid, 0.55)
        expected = 1.0 / (1.0 + 10 ** ((r - ability[uid]) / 0.4))
        result = VERDICT_SCORE.get(verdict, score)
        rating[qid] = min(0.99, max(0.01, r + k * (expected - result)))
        ability[uid] = min(0.99, max(0.01, ability[uid] + k * (result - expected)))
    out = {}
    for qid in diff:
        s = stats.get(qid)
        n = s["attempts"] if s else 0
        out[qid] = {
            "attempts": n,
            "learners": len(s["learners"]) if s else 0,
            "pass_rate": round(s["correct"] / n, 3) if n else None,
            "fail_rate": round(s["incorrect"] / n, 3) if n else None,
            "partial": s["partially_correct"] if s else 0,
            "rating": round(rating[qid] * 1000),
        }
    return out


# ----------------------------------------------------------------------------- overview

def _manila_day(dt: datetime) -> str:
    return dt.astimezone(MANILA).date().isoformat()


def overview(db: Session, *, days: int = 30, now: datetime | None = None) -> dict:
    now = _now(now)
    answers = _answers(db)
    runs = [(uid, slug, _aware(at), passed, total) for uid, slug, at, passed, total in
            db.query(ExerciseAttempt.user_id, ExerciseAttempt.slug, ExerciseAttempt.created_at,
                     ExerciseAttempt.passed, ExerciseAttempt.total)]
    learners = db.query(func.count(User.id)).scalar() or 0
    new_7 = sum(1 for (c,) in db.query(User.created_at) if _aware(c) and _aware(c) >= now - timedelta(days=7))

    def active(since: datetime) -> int:
        return len({a[1] for a in answers if a[3] >= since} | {r[0] for r in runs if r[2] >= since})

    n = len(answers)
    verdicts = defaultdict(int)
    for a in answers:
        verdicts[a[4]] += 1
    solved_runs = sum(1 for r in runs if r[4] and r[3] == r[4])

    # Daily activity, Manila days, oldest first.
    today = now.astimezone(MANILA).date()
    day_keys = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
    daily = {d: {"date": d, "answers": 0, "runs": 0, "learners": set()} for d in day_keys}
    for _rid, uid, _qid, at, _v, _s in answers:
        d = daily.get(_manila_day(at))
        if d:
            d["answers"] += 1
            d["learners"].add(uid)
    for uid, _slug, at, _p, _t in runs:
        d = daily.get(_manila_day(at))
        if d:
            d["runs"] += 1
            d["learners"].add(uid)

    # Attempts by topic and by language.
    qinfo = {qid: (slug, name, lang, (rub or {}).get("kind") or "explain", title)
             for qid, slug, name, lang, rub, title in
             db.query(Question.id, SkillDomain.slug, SkillDomain.name, Question.language, Question.rubric, Question.title)
             .join(SkillDomain, SkillDomain.id == Question.domain_id)}
    topic = defaultdict(lambda: [0, 0])
    lang = defaultdict(lambda: [0, 0])
    topic_names = {}
    for _rid, _uid, qid, _at, v, _s in answers:
        info = qinfo.get(qid)
        if not info:
            continue
        slug, name, language, kind, _t = info
        key = "fill_blank" if kind == "fill_blank" else slug
        topic_names[key] = "Fill in the code" if kind == "fill_blank" else name
        for bucket, k in ((topic, key), (lang, language)):
            bucket[k][0] += 1
            bucket[k][1] += v == "correct"
    ex_topic = defaultdict(lambda: [0, 0])
    for _uid, slug, _at, passed, total in runs:
        ex = BY_SLUG.get(slug)
        k = ex.get("topic", "Other") if ex else "Other"
        ex_topic[k][0] += 1
        ex_topic[k][1] += bool(total) and passed == total

    def bars(d: dict, labels) -> list[dict]:
        return sorted(({"key": k, "label": labels(k), "attempts": a, "accuracy": round(c / a, 3) if a else None}
                       for k, (a, c) in d.items()), key=lambda b: -b["attempts"])

    stats = question_stats(db, answers)
    hardest = sorted(
        ((qid, s) for qid, s in stats.items() if s["attempts"] >= HARDEST_MIN_ATTEMPTS and qid in qinfo),
        key=lambda t: (-(t[1]["fail_rate"] or 0), -t[1]["attempts"]),
    )[:8]
    feedback_total = db.query(func.count(UserFeedback.id)).scalar() or 0
    reviewed = db.query(func.count(FeedbackModeration.feedback_id)).filter(FeedbackModeration.reviewed_at.isnot(None)).scalar() or 0
    return {
        "totals": {
            "learners": learners, "new_7d": new_7,
            "active_7d": active(now - timedelta(days=7)), "active_30d": active(now - timedelta(days=30)),
            "attempts": n, "attempts_7d": sum(1 for a in answers if a[3] >= now - timedelta(days=7)),
            "accuracy": round(verdicts["correct"] / n, 3) if n else None,
            "partial_rate": round(verdicts["partially_correct"] / n, 3) if n else None,
            "exercise_runs": len(runs), "exercise_solve_rate": round(solved_runs / len(runs), 3) if runs else None,
            "feedback": feedback_total, "feedback_unreviewed": max(0, feedback_total - reviewed),
        },
        "daily": [{**d, "learners": len(d["learners"])} for d in daily.values()],
        "by_topic": bars(topic, lambda k: topic_names.get(k, k)),
        "by_language": bars(lang, lambda k: LANGUAGE_LABELS.get(k, k)),
        "exercises_by_topic": bars(ex_topic, lambda k: k),
        "hardest": [{"id": qid, "title": qinfo[qid][4], "topic": qinfo[qid][1],
                     "language": LANGUAGE_LABELS.get(qinfo[qid][2], qinfo[qid][2]), **s} for qid, s in hardest],
        "hardest_min_attempts": HARDEST_MIN_ATTEMPTS,
    }


# ----------------------------------------------------------------------------- learners

LEARNER_SORTS = ("recent", "xp", "attempts", "joined", "name")


def _learner_rows(db: Session) -> list[dict]:
    users = db.query(User).all()
    profiles = {p.user_id: p for p in db.query(LearnerProfile)}
    settings = {s.user_id: s for s in db.query(UserSettings)}
    flags = {f.user_id: f for f in db.query(LearnerFlag)}
    xp = {uid: int(x or 0) for uid, x in db.query(XpEvent.user_id, func.sum(XpEvent.amount)).group_by(XpEvent.user_id)}
    attempts = dict(db.query(Response.user_id, func.count(Response.id)).group_by(Response.user_id).all())
    runs = dict(db.query(ExerciseAttempt.user_id, func.count(ExerciseAttempt.id)).group_by(ExerciseAttempt.user_id).all())
    last_a = dict(db.query(Response.user_id, func.max(Response.created_at)).group_by(Response.user_id).all())
    last_r = dict(db.query(ExerciseAttempt.user_id, func.max(ExerciseAttempt.created_at)).group_by(ExerciseAttempt.user_id).all())
    admins = get_settings().admin_identity_set
    out = []
    for u in users:
        p, st, fl = profiles.get(u.id), settings.get(u.id), flags.get(u.id)
        chosen = st.display_name if st and st.display_name else ""
        total = xp.get(u.id, 0)
        lasts = [d for d in (_aware(last_a.get(u.id)), _aware(last_r.get(u.id))) if d]
        level = level_for(total)
        out.append({
            "id": u.id,
            "name": chosen or u.display_name,
            "handle": p.handle if p else None,
            "confirm_word": p.handle if p else str(u.id),
            "board_name": public_name(p, u, chosen) if p else None,
            "visibility": p.visibility if p else "handle",
            "email": u.email,
            "provider": u.auth_provider,
            "identity": identity(u),
            "avatar_url": u.avatar_url,
            "avatar": st.avatar if st and st.avatar and st.avatar != "photo" else None,
            "xp": total, "level": level, "level_name": level_name(level),
            "attempts": int(attempts.get(u.id, 0)), "exercise_runs": int(runs.get(u.id, 0)),
            "last_active": max(lasts) if lasts else None,
            "joined": _aware(u.created_at),
            "board_hidden": bool(fl and fl.board_hidden),
            "is_admin": identity(u) in admins,
        })
    return out


def learners(db: Session, *, q: str = "", sort: str = "recent", page: int = 1, size: int = 20) -> dict:
    rows = _learner_rows(db)
    total_all = len(rows)
    needle = q.strip().lower().lstrip("@")
    if needle:
        rows = [r for r in rows if any(needle in (r[k] or "").lower() for k in ("name", "handle", "email", "identity"))]
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    keys = {
        "recent": lambda r: (-(r["last_active"] or epoch).timestamp(), r["id"]),
        "xp": lambda r: (-r["xp"], r["id"]),
        "attempts": lambda r: (-(r["attempts"] + r["exercise_runs"]), r["id"]),
        "joined": lambda r: (-(r["joined"] or epoch).timestamp(), r["id"]),
        "name": lambda r: (r["name"].lower(), r["id"]),
    }
    rows.sort(key=keys.get(sort, keys["recent"]))
    total = len(rows)
    return {"items": rows[(page - 1) * size: page * size], "total": total, "total_all": total_all,
            "page": page, "pages": max(1, math.ceil(total / size))}


def learner_row(db: Session, user_id: int) -> dict | None:
    return next((r for r in _learner_rows(db) if r["id"] == user_id), None)


def learner_label(db: Session, user: User) -> str:
    p = db.get(LearnerProfile, user.id)
    return f"learner #{user.id}" + (f" (@{p.handle})" if p else "")


def confirm_word(db: Session, user: User) -> str:
    """What the admin types to confirm a destructive action: the learner's handle (or id)."""
    p = db.get(LearnerProfile, user.id)
    return p.handle if p else str(user.id)


def set_board_hidden(db: Session, user: User, hidden: bool) -> bool:
    fl = db.get(LearnerFlag, user.id)
    if fl is None:
        fl = LearnerFlag(user_id=user.id, board_hidden=0)
        db.add(fl)
    changed = bool(fl.board_hidden) != hidden
    fl.board_hidden = 1 if hidden else 0
    return changed


def reset_xp(db: Session, user: User) -> int:
    """Zero the learner's XP. The award rows stay (at 0) so the same work isn't awarded again;
    new activity earns XP as usual. Badges are kept."""
    events = db.query(XpEvent).filter(XpEvent.user_id == user.id).all()
    before = sum(e.amount or 0 for e in events)
    for e in events:
        e.amount = 0
    return before


# ----------------------------------------------------------------------------- questions

QUESTION_SORTS = ("id", "attempts", "pass_rate", "fail_rate", "rating")


def _question_row(q: Question, d: SkillDomain, e: QuestionEdit | None, s: dict) -> dict:
    rub = q.rubric or {}
    return {
        "id": q.id, "title": q.title, "language": q.language,
        "language_label": LANGUAGE_LABELS.get(q.language, q.language),
        "topic": d.slug, "topic_label": d.name, "difficulty": _enum(q.difficulty),
        "kind": rub.get("kind") or "explain", "source": q.source,
        "hidden": bool(e and e.hidden),
        "edited": bool(e and (e.question_text is not None or e.reference_answer is not None or e.key_idea is not None)),
        "preview": split_prompt(q.prompt)[0][:160],
        **s,
    }


def questions(db: Session, *, topic: str = "", language: str = "", difficulty: str = "", kind: str = "",
              status: str = "", q: str = "", sort: str = "id", page: int = 1, size: int = 25) -> dict:
    stats = question_stats(db)
    edits = {e.question_id: e for e in db.query(QuestionEdit)}
    rows = db.query(Question, SkillDomain).join(SkillDomain, SkillDomain.id == Question.domain_id).all()
    out = [_question_row(qq, d, edits.get(qq.id), stats.get(qq.id, {})) for qq, d in rows]
    needle = q.strip().lower()
    out = [r for r in out if (not topic or r["topic"] == topic) and (not language or r["language"] == language)
           and (not difficulty or r["difficulty"] == difficulty) and (not kind or r["kind"] == kind)
           and (not status or (status == "hidden" and r["hidden"]) or (status == "visible" and not r["hidden"])
                or (status == "edited" and r["edited"]) or (status == "new" and r["source"] == "admin"))
           and (not needle or needle in r["title"].lower() or needle in r["preview"].lower() or needle == str(r["id"]))]
    if sort == "id":
        out.sort(key=lambda r: r["id"])
    else:
        out.sort(key=lambda r: (r.get(sort) is None, -(r.get(sort) or 0), r["id"]))
    total = len(out)
    domains = [{"slug": d.slug, "name": d.name} for d in db.query(SkillDomain).order_by(SkillDomain.name)]
    langs = sorted({r[0] for r in db.query(Question.language).distinct()})
    return {"items": out[(page - 1) * size: page * size], "total": total, "page": page,
            "pages": max(1, math.ceil(total / size)), "topics": domains,
            "languages": [{"key": k, "label": LANGUAGE_LABELS.get(k, k)} for k in langs]}


def question_detail(db: Session, qid: int) -> dict | None:
    row = db.query(Question, SkillDomain).join(SkillDomain, SkillDomain.id == Question.domain_id).filter(Question.id == qid).first()
    if row is None:
        return None
    q, d = row
    e = db.get(QuestionEdit, qid)
    s = question_stats(db).get(qid, {})
    rub = q.rubric or {}
    text, task = split_prompt(q.prompt)
    return {
        **_question_row(q, d, e, s),
        "code": q.code or "",
        "question_text": text, "task_line": task,
        "reference_answer": rub.get("reference_answer", ""),
        "key_idea": key_idea_of(rub),
        "hints": rub.get("hints") or [],
        "key_points": [c.get("label") for c in rub.get("concepts") or []],
        "accepted_answers": rub.get("accepted_answers") or [],
        "edited_at": _aware(e.updated_at) if e else None,
    }


def exercises(db: Session) -> list[dict]:
    rows = db.query(ExerciseAttempt.slug, ExerciseAttempt.user_id, ExerciseAttempt.passed, ExerciseAttempt.total).all()
    agg: dict[str, dict] = {}
    for slug, uid, passed, total in rows:
        a = agg.setdefault(slug, {"runs": 0, "passing_runs": 0, "learners": set(), "solvers": set()})
        a["runs"] += 1
        a["learners"].add(uid)
        if total and passed == total:
            a["passing_runs"] += 1
            a["solvers"].add(uid)
    out = []
    for slug, ex in BY_SLUG.items():
        a = agg.get(slug)
        n = len(a["learners"]) if a else 0
        out.append({
            "slug": slug, "title": ex["title"], "language": ex["language"],
            "language_label": LANGUAGE_LABELS.get(ex["language"], ex["language"]),
            "difficulty": ex.get("difficulty", ""), "topic": ex.get("topic", ""),
            "runs": a["runs"] if a else 0, "learners": n, "solvers": len(a["solvers"]) if a else 0,
            "solve_rate": round(len(a["solvers"]) / n, 3) if n else None,
            "run_pass_rate": round(a["passing_runs"] / a["runs"], 3) if a else None,
        })
    return out


# ----------------------------------------------------------------------------- feedback

def feedback(db: Session, *, status: str = "", category: str = "", rating: int | None = None, q: str = "",
             page: int = 1, size: int = 20) -> dict:
    query = (db.query(UserFeedback, User, LearnerProfile, UserSettings, FeedbackModeration)
             .join(User, User.id == UserFeedback.user_id)
             .outerjoin(LearnerProfile, LearnerProfile.user_id == User.id)
             .outerjoin(UserSettings, UserSettings.user_id == User.id)
             .outerjoin(FeedbackModeration, FeedbackModeration.feedback_id == UserFeedback.id))
    if status == "new":
        query = query.filter(or_(FeedbackModeration.reviewed_at.is_(None), FeedbackModeration.feedback_id.is_(None)))
    elif status == "reviewed":
        query = query.filter(FeedbackModeration.reviewed_at.isnot(None))
    elif status == "hidden":
        query = query.filter(FeedbackModeration.hidden == 1)
    if category:
        query = query.filter(UserFeedback.category == category)
    if rating:
        query = query.filter(UserFeedback.rating == rating)
    if q.strip():
        query = query.filter(UserFeedback.message.ilike(f"%{q.strip()}%"))
    total = query.count()
    rows = query.order_by(UserFeedback.created_at.desc(), UserFeedback.id.desc()).offset((page - 1) * size).limit(size).all()
    cats = [c for (c,) in db.query(UserFeedback.category).distinct().order_by(UserFeedback.category)]
    return {
        "items": [{
            "id": f.id, "rating": f.rating, "category": f.category, "message": f.message,
            "page_context": f.page_context, "created_at": _aware(f.created_at),
            "author": {"id": u.id, "name": (st.display_name if st and st.display_name else u.display_name),
                       "handle": p.handle if p else None},
            "reviewed_at": _aware(m.reviewed_at) if m else None, "hidden": bool(m and m.hidden),
        } for f, u, p, st, m in rows],
        "total": total, "page": page, "pages": max(1, math.ceil(total / size)), "categories": cats,
    }


def moderation(db: Session, fb: UserFeedback) -> FeedbackModeration:
    m = db.get(FeedbackModeration, fb.id)
    if m is None:
        m = FeedbackModeration(feedback_id=fb.id, hidden=0)
        db.add(m)
    return m
