"""XP, levels, badges and the leaderboard.

Everything is worked out from the learner's history (answers, hints, daily challenges and
coding exercises), so it's retroactive: the first sync counts what a learner already did.
Each award has a stable key and is stored once in ``xp_events``; ``sync_user`` only adds
what's missing, so it's safe to call as often as we like.

XP rules
--------
- Correct answer, first time per question: 10 / 20 / 30 (beginner / intermediate / advanced).
  Each hint used on it takes 10% off (at most 30%), like the score penalty.
- Coding exercise passed, first time: 30 / 50 / 80. Each hint opened before passing takes 10% off,
  and passing after opening the solution ("Solved with help") takes 25% off (at most 50% in total).
- Daily challenge done: +15 per day.
- Streak bonus: +5 for each day the streak has run before today, up to +30 (day 2 = +5, day 7+ = +30).
- Learning paths: +25 for each step done, +100 for finishing a path (see app/services/paths.py).
- Mistake review: +5 the first time each mistake is fixed (once per item, ever; see services/review.py).
- Timed quiz: +3 extra for a question whose first correct answer was in a quiz (see services/quiz.py).

Levels: reaching level L takes 50 × L × (L − 1) XP in total (100, 300, 600, 1000, ...).
"""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content.exercises import BY_SLUG
from app.models.models import (
    AppMeta,
    DailyCompletion,
    ExerciseAttempt,
    ExerciseHelp,
    Feedback,
    LearnerProfile,
    Question,
    Response,
    SkillDomain,
    SkillMastery,
    User,
    UserBadge,
    XpEvent,
)
from app.services.daily import MANILA, manila_today

logger = logging.getLogger(__name__)

ANSWER_XP = {"beginner": 10, "intermediate": 20, "advanced": 30}
EXERCISE_XP = {"beginner": 30, "intermediate": 50, "advanced": 80}
DAILY_XP = 15
STREAK_STEP, STREAK_MAX = 5, 30
HINT_CUT, HINT_CUT_MAX = 0.10, 0.30
HELP_CUT, TOTAL_CUT_MAX = 0.25, 0.50
CODE_LANGUAGES = ["python", "javascript", "cpp", "java", "php"]
LANGUAGE_NAMES = {"python": "Python", "javascript": "JavaScript", "cpp": "C++", "java": "Java", "php": "PHP"}
DIFF_NAMES = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"}

# ----------------------------------------------------------------------------- levels

LEVEL_NAMES = [
    "Initiate", "Tracer", "Debugger", "Builder", "Solver",
    "Architect", "Optimizer", "Logician", "Limit Breaker", "Limitless",
]


def level_floor(level: int) -> int:
    """Total XP needed to reach ``level`` (level 1 starts at 0)."""
    return 50 * level * (level - 1)


def level_for(xp: int) -> int:
    level = 1
    while xp >= level_floor(level + 1):
        level += 1
    return level


def level_name(level: int) -> str:
    return LEVEL_NAMES[min(level, len(LEVEL_NAMES)) - 1]


def level_info(xp: int) -> dict:
    level = level_for(xp)
    floor, nxt = level_floor(level), level_floor(level + 1)
    return {
        "xp": xp, "level": level, "level_name": level_name(level), "next_level_name": level_name(level + 1),
        "level_floor": floor, "next_level_at": nxt, "to_next": nxt - xp,
        "progress": round((xp - floor) / (nxt - floor), 4),
    }


# ----------------------------------------------------------------------------- badges

@dataclass(frozen=True)
class Badge:
    key: str
    name: str
    description: str
    group: str  # answers | streaks | languages | code | paths | review


BADGES: list[Badge] = [
    Badge("first-correct", "First Build", "Get your first answer right.", "answers"),
    Badge("ten-correct", "Ten Clean Runs", "Get 10 different questions right.", "answers"),
    Badge("fifty-correct", "Fifty Proofs", "Get 50 different questions right.", "answers"),
    Badge("advanced", "Deep End", "Get an advanced question right.", "answers"),
    Badge("mastery", "Topic Master", "Reach 80% mastery in a topic, over at least 5 answers.", "answers"),
    Badge("daily-first", "Daily Driver", "Finish a daily challenge.", "streaks"),
    Badge("streak-3", "Spark", "Keep a 3-day daily streak.", "streaks"),
    Badge("streak-7", "Full Week", "Keep a 7-day daily streak.", "streaks"),
    Badge("streak-30", "Unbroken", "Keep a 30-day daily streak.", "streaks"),
    Badge("cpp-answer", "Pointer Sense", "Get a C++ question right.", "languages"),
    Badge("java-answer", "Class Act", "Get a Java question right.", "languages"),
    Badge("oop-answer", "Object Thinker", "Get an object-oriented programming question right.", "languages"),
    Badge("filipino", "Sariling Wika", "Get a question right with an answer in Filipino or Taglish.", "languages"),
    Badge("ex-python", "Python Coder", "Pass your first Python coding exercise.", "code"),
    Badge("ex-javascript", "JavaScript Coder", "Pass your first JavaScript coding exercise.", "code"),
    Badge("ex-cpp", "C++ Coder", "Pass your first C++ coding exercise.", "code"),
    Badge("ex-java", "Java Coder", "Pass your first Java coding exercise.", "code"),
    Badge("ex-php", "PHP Coder", "Pass your first PHP coding exercise.", "code"),
    Badge("unassisted", "Unassisted", "Pass a coding exercise without opening a hint or the solution.", "code"),
    Badge("polyglot", "Polyglot", "Pass a coding exercise in all five languages.", "code"),
]
# Learning-path badges live in their own list (the 20 above are the core set).
PATH_BADGES: list[Badge] = [
    Badge("path-step", "Trailhead", "Finish a step in any learning path.", "paths"),
    Badge("path-finisher", "Path Finisher", "Finish every step of a learning path.", "paths"),
    Badge("path-three", "Wayfinder", "Finish three learning paths.", "paths"),
]
# Mistake review and timed quiz badges.
REVIEW_BADGES: list[Badge] = [
    Badge("second-look", "Second Look", "Fix 10 mistakes from Review mistakes.", "review"),
    Badge("beat-the-clock", "Beat the Clock", "Score 80% or more on a timed quiz of 10 or more questions.", "review"),
]
ALL_BADGES: list[Badge] = BADGES + PATH_BADGES + REVIEW_BADGES
BADGE_BY_KEY = {b.key: b for b in ALL_BADGES}
PATH_KINDS = ("path_step", "path")
REVIEW_KINDS = ("fix", "quiz")
REVIEW_BADGE_KEYS = {b.key for b in REVIEW_BADGES}


# ----------------------------------------------------------------------------- time helpers

def _aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def week_start(now: datetime | None = None) -> datetime:
    """Monday 00:00 in Asia/Manila for the week containing ``now``, as an aware UTC datetime."""
    today = manila_today(now)
    monday = today - timedelta(days=today.weekday())
    return datetime(monday.year, monday.month, monday.day, tzinfo=MANILA).astimezone(timezone.utc)


def _db_time(db: Session, dt: datetime) -> datetime:
    # SQLite stores these columns as naive UTC; Postgres compares aware datetimes properly.
    return dt.replace(tzinfo=None) if db.get_bind().dialect.name == "sqlite" else dt


def _cut(amount: int, fraction: float) -> int:
    return max(1, round(amount * (1 - fraction)))


# ----------------------------------------------------------------------------- what history earns

@dataclass
class Earned:
    events: dict[str, tuple[str, int, str, datetime]] = field(default_factory=dict)  # key -> (kind, amount, label, when)
    badges: dict[str, datetime] = field(default_factory=dict)

    def badge(self, key: str, when: datetime) -> None:
        if key not in self.badges or when < self.badges[key]:
            self.badges[key] = when


def _diff(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def compute(db: Session, user: User, now: datetime | None = None) -> Earned:
    """Every award and badge the learner's history earns (pure read, nothing is written)."""
    out = Earned()
    now = _aware(now)

    # Answers: the first correct answer to each question (answers in a quiz that's still
    # hiding its results don't count until it ends).
    from app.services import quiz, review

    hidden = review.hidden_response_ids(db, user.id, now)
    first_correct: dict[int, tuple[int, datetime, str]] = {}
    rows = (
        db.query(Response.id, Response.question_id, Response.created_at, Feedback.details,
                 Question.language, Question.difficulty, Question.title, SkillDomain.slug)
        .join(Feedback, Feedback.response_id == Response.id)
        .join(Question, Question.id == Response.question_id)
        .join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Response.user_id == user.id)
        .order_by(Response.created_at.asc(), Response.id.asc())
        .all()
    )
    correct_times: list[datetime] = []
    for rid, qid, created, details, lang, diff, title, domain in rows:
        details = details or {}
        if details.get("verdict") != "correct" or rid in hidden:
            continue
        when = _aware(created)
        key = f"answer:{qid}"
        if key in out.events:
            continue
        d = _diff(diff)
        hints_used = int(details.get("hints_used") or 0)
        base = ANSWER_XP.get(d, ANSWER_XP["intermediate"])
        amount = _cut(base, min(HINT_CUT_MAX, HINT_CUT * hints_used)) if hints_used else base
        label = f"Correct: {title}" + (f" ({hints_used} hint{'s' if hints_used != 1 else ''})" if hints_used else "")
        out.events[key] = ("answer", amount, label[:200], when)
        first_correct[qid] = (rid, when, title)
        correct_times.append(when)
        if d == "advanced":
            out.badge("advanced", when)
        if lang == "cpp":
            out.badge("cpp-answer", when)
        if lang == "java":
            out.badge("java-answer", when)
        if domain == "oop":
            out.badge("oop-answer", when)
        if details.get("answer_language") in ("fil", "taglish"):
            out.badge("filipino", when)
    for n, key in ((1, "first-correct"), (10, "ten-correct"), (50, "fifty-correct")):
        if len(correct_times) >= n:
            out.badge(key, correct_times[n - 1])

    # Mastery has no history of its own, so the badge is dated when it's first seen.
    strong = (
        db.query(SkillMastery.id)
        .filter(SkillMastery.user_id == user.id, SkillMastery.mastery >= 0.8, SkillMastery.attempts >= 5)
        .first()
    )
    if strong:
        out.badge("mastery", now)

    # Daily challenges and streaks.
    days = (
        db.query(DailyCompletion.day, DailyCompletion.created_at)
        .filter(DailyCompletion.user_id == user.id)
        .order_by(DailyCompletion.day.asc())
        .all()
    )
    prev: date | None = None
    run = 0
    for day_str, created in days:
        day = date.fromisoformat(day_str)
        when = _aware(created)
        run = run + 1 if prev is not None and day - prev == timedelta(days=1) else 1
        prev = day
        out.events[f"daily:{day_str}"] = ("daily", DAILY_XP, "Daily challenge", when)
        if run >= 2:
            bonus = min(STREAK_MAX, STREAK_STEP * (run - 1))
            out.events[f"streak:{day_str}"] = ("streak", bonus, f"{run}-day streak bonus", when)
        out.badge("daily-first", when)
        for n in (3, 7, 30):
            if run >= n:
                out.badge(f"streak-{n}", when)

    # Coding exercises: the first run that passed every test.
    attempts = (
        db.query(ExerciseAttempt.slug, ExerciseAttempt.passed, ExerciseAttempt.created_at)
        .filter(ExerciseAttempt.user_id == user.id)
        .order_by(ExerciseAttempt.created_at.asc(), ExerciseAttempt.id.asc())
        .all()
    )
    help_rows = db.query(ExerciseHelp).filter(ExerciseHelp.user_id == user.id).all()
    hints_before: dict[str, int] = {}
    helped: set[str] = set()
    any_help: set[str] = set()
    for h in help_rows:
        any_help.add(h.slug)
        if h.kind == "hint" and h.before_pass:
            hints_before[h.slug] = max(hints_before.get(h.slug, 0), int(h.level or 0))
        if h.kind == "solution" and h.before_pass:
            helped.add(h.slug)
    passed_langs: dict[str, datetime] = {}
    for slug, passed, created in attempts:
        e = BY_SLUG.get(slug)
        key = f"exercise:{slug}"
        if not e or key in out.events or passed < len(e["tests"]):
            continue
        when = _aware(created)
        base = EXERCISE_XP.get(e["difficulty"], EXERCISE_XP["intermediate"])
        n_hints = hints_before.get(slug, 0)
        cut = min(TOTAL_CUT_MAX, min(HINT_CUT_MAX, HINT_CUT * n_hints) + (HELP_CUT if slug in helped else 0))
        amount = _cut(base, cut) if cut else base
        note = "solved with help" if slug in helped else (f"{n_hints} hint{'s' if n_hints != 1 else ''}" if n_hints else "")
        label = f"Passed: {e['title']} ({LANGUAGE_NAMES.get(e['language'], e['language'])})" + (f", {note}" if note else "")
        out.events[key] = ("exercise", amount, label[:200], when)
        lang = e["language"]
        if lang in CODE_LANGUAGES:
            out.badge(f"ex-{lang}", when)
            passed_langs.setdefault(lang, when)
        if slug not in any_help:
            out.badge("unassisted", when)
    if all(lang in passed_langs for lang in CODE_LANGUAGES):
        out.badge("polyglot", max(passed_langs.values()))

    # Learning paths: steps and whole paths finished (worked out from the same history).
    from app.services import paths

    path_events, path_badges = paths.awards(db, user)
    out.events.update(path_events)
    for key, when in path_badges.items():
        out.badge(key, when)

    # Mistake review fixes and timed quizzes.
    for events, badges in (review.awards(db, user), quiz.awards(db, user, first_correct)):
        out.events.update(events)
        for key, when in badges.items():
            out.badge(key, when)
    return out


# ----------------------------------------------------------------------------- profiles

ADJECTIVES = [
    "Swift", "Quiet", "Bright", "Steady", "Sharp", "Bold", "Calm", "Clever",
    "Keen", "Nimble", "Brave", "Lucid", "Rapid", "Silent", "Solid", "Agile",
]
NOUNS = [
    "Compiler", "Parser", "Tracer", "Debugger", "Kernel", "Vector", "Lambda", "Pointer",
    "Circuit", "Thread", "Signal", "Stack", "Token", "Branch", "Router", "Cursor",
]
VISIBILITY = ("handle", "name", "anonymous", "hidden")


def new_handle(db: Session) -> str:
    """A random, non-identifying handle like "Swift Parser 42" (never based on the learner's name)."""
    for _ in range(50):
        handle = f"{secrets.choice(ADJECTIVES)} {secrets.choice(NOUNS)} {secrets.randbelow(90) + 10}"
        if not db.query(LearnerProfile.user_id).filter_by(handle=handle).first():
            return handle
    return f"Learner {secrets.token_hex(3)}"


def ensure_profile(db: Session, user: User) -> LearnerProfile:
    """The learner's leaderboard profile, created (and committed) on first use.

    The header and the page can ask for it at the same moment on a first visit, so a
    lost race just reads the profile the other request created.
    """
    profile = db.get(LearnerProfile, user.id)
    if profile is not None:
        return profile
    for _ in range(3):
        db.add(LearnerProfile(user_id=user.id, handle=new_handle(db), visibility="handle"))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
        profile = db.get(LearnerProfile, user.id)
        if profile is not None:
            return profile
    raise RuntimeError("Couldn't create a leaderboard profile")


def _safe_name(user: User) -> str:
    """The learner's own display name, only when they chose to show it. Never an email."""
    name = (user.display_name or "").strip()
    if not name or "@" in name:
        return ""
    # With no name from GitHub/Google, the display name falls back to the email's first part: never show that.
    if user.email and name.lower() == user.email.split("@")[0].strip().lower():
        return ""
    return name[:40]


def public_name(profile: LearnerProfile, user: User) -> str:
    if profile.visibility == "name":
        return _safe_name(user) or profile.handle
    if profile.visibility == "anonymous":
        return "Anonymous learner"
    return profile.handle


# ----------------------------------------------------------------------------- sync

@dataclass
class SyncResult:
    events: list[XpEvent]
    badges: list[UserBadge]


def sync_user(db: Session, user: User, now: datetime | None = None) -> SyncResult:
    """Store any XP and badges the learner has earned but doesn't have yet. Idempotent."""
    # The very first sync for a learner counts their past work ("retro"); after that it's new work.
    retro = 1 if db.get(LearnerProfile, user.id) is None else 0
    ensure_profile(db, user)
    earned = compute(db, user, now)
    have = {k for (k,) in db.query(XpEvent.key).filter(XpEvent.user_id == user.id).all()}
    have_badges = {k for (k,) in db.query(UserBadge.badge).filter(UserBadge.user_id == user.id).all()}
    stamp = _aware(now)
    # Path awards for work done before paths existed are past work too, even for known learners.
    from app.services import paths

    # Likewise review fixes made before mistake review existed.
    launches = {"paths": paths.launched_at(db), "review": launched_at(db, REVIEW_LAUNCH_KEY)}

    def is_retro(feature: str | None, when: datetime) -> int:
        launch = launches.get(feature) if feature else None
        return 1 if retro or (launch is not None and _aware(when) < launch) else 0

    def event_feature(kind: str) -> str | None:
        return "paths" if kind in PATH_KINDS else "review" if kind in REVIEW_KINDS else None

    def badge_feature(key: str) -> str | None:
        return "paths" if key.startswith("path-") else "review" if key in REVIEW_BADGE_KEYS else None

    new_events = [
        XpEvent(user_id=user.id, key=key, kind=kind, amount=amount, label=label,
                retro=is_retro(event_feature(kind), when), created_at=when, awarded_at=stamp)
        for key, (kind, amount, label, when) in earned.events.items() if key not in have
    ]
    new_badges = [
        UserBadge(user_id=user.id, badge=key, retro=is_retro(badge_feature(key), when), earned_at=when)
        for key, when in earned.badges.items() if key not in have_badges and key in BADGE_BY_KEY
    ]
    db.add_all(new_events + new_badges)
    try:
        db.commit()
    except IntegrityError:  # another request synced the same awards at the same moment
        db.rollback()
        return SyncResult([], [])
    return SyncResult(new_events, new_badges)


REVIEW_LAUNCH_KEY = "review_launched_at"


def launched_at(db: Session, key: str) -> datetime | None:
    """When a feature went live on this database (awards for older work are "past work")."""
    meta = db.get(AppMeta, key)
    try:
        return _aware(datetime.fromisoformat(meta.value)) if meta else None
    except ValueError:
        return None


def mark_launch(db: Session, key: str) -> None:
    if db.get(AppMeta, key) is None:
        db.add(AppMeta(key=key, value=datetime.now(timezone.utc).isoformat()))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()


def safe_sync(db: Session, user: User) -> None:
    """Sync after an answer or exercise run; never lets XP trouble break the learner's request."""
    try:
        sync_user(db, user)
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("XP sync failed for user %s", user.id)


def backfill_all(db: Session) -> int:
    """Count past work for every learner (run once at startup)."""
    n = 0
    for user in db.query(User).all():
        sync_user(db, user)
        n += 1
    return n


# ----------------------------------------------------------------------------- read models

def total_xp(db: Session, user_id: int, since: datetime | None = None) -> int:
    q = db.query(func.coalesce(func.sum(XpEvent.amount), 0)).filter(XpEvent.user_id == user_id)
    if since is not None:
        q = q.filter(XpEvent.created_at >= _db_time(db, since))
    return int(q.scalar() or 0)


def badge_list(db: Session, user: User) -> list[dict]:
    earned = {b.badge: _aware(b.earned_at) for b in db.query(UserBadge).filter(UserBadge.user_id == user.id).all()}
    return [
        {"key": b.key, "name": b.name, "description": b.description, "group": b.group,
         "earned": b.key in earned, "earned_at": earned.get(b.key)}
        for b in ALL_BADGES
    ]


def summary(db: Session, user: User, now: datetime | None = None) -> dict:
    xp = total_xp(db, user.id)
    week = total_xp(db, user.id, week_start(now))
    badges = badge_list(db, user)
    recent = (
        db.query(XpEvent).filter(XpEvent.user_id == user.id)
        .order_by(XpEvent.created_at.desc(), XpEvent.id.desc()).limit(8).all()
    )
    return {
        **level_info(xp),
        "xp_this_week": week,
        "badges": badges,
        "badges_earned": sum(1 for b in badges if b["earned"]),
        "recent": [{"label": e.label, "amount": e.amount, "kind": e.kind, "created_at": _aware(e.created_at)} for e in recent],
    }


def news(db: Session, user: User) -> dict:
    """XP and badges the learner hasn't been told about yet; marks them as told."""
    events = db.query(XpEvent).filter(XpEvent.user_id == user.id, XpEvent.notified == 0).all()
    badges = db.query(UserBadge).filter(UserBadge.user_id == user.id, UserBadge.notified == 0).all()
    out = {
        "xp": sum(e.amount for e in events),
        "retro": any(e.retro for e in events) or any(b.retro for b in badges),
        "items": [{"label": e.label, "amount": e.amount} for e in sorted(events, key=lambda e: _aware(e.created_at))][-5:],
        "badges": [{"key": b.badge, "name": BADGE_BY_KEY[b.badge].name, "description": BADGE_BY_KEY[b.badge].description}
                   for b in badges if b.badge in BADGE_BY_KEY],
    }
    for row in [*events, *badges]:
        row.notified = 1
    db.commit()
    return out


LEADERBOARD_SIZE = 50


def leaderboard(db: Session, user: User, period: str, now: datetime | None = None) -> dict:
    """Top learners by XP for this Manila week or all time, plus the learner's own rank.

    Learners who chose "hidden" are left out (and don't push anyone else down). Emails are never used.
    """
    start = week_start(now) if period == "week" else None
    q = db.query(XpEvent.user_id, func.sum(XpEvent.amount).label("xp"))
    if start is not None:
        q = q.filter(XpEvent.created_at >= _db_time(db, start))
    totals = {uid: int(xp or 0) for uid, xp in q.group_by(XpEvent.user_id).all()}
    profiles = {p.user_id: p for p in db.query(LearnerProfile).filter(LearnerProfile.user_id.in_(list(totals) or [0])).all()}
    users = {u.id: u for u in db.query(User).filter(User.id.in_(list(totals) or [0])).all()}
    all_xp = _all_time(db, list(totals)) if start is not None else totals

    visible = [
        (uid, xp) for uid, xp in totals.items()
        if xp > 0 and uid in users and (uid not in profiles or profiles[uid].visibility != "hidden")
    ]
    visible.sort(key=lambda t: (-t[1], t[0]))

    def rank_of(xp: int) -> int:
        return 1 + sum(1 for _, other in visible if other > xp)

    def entry(uid: int, xp: int) -> dict:
        p = profiles.get(uid)
        name = public_name(p, users[uid]) if p else "Anonymous learner"
        level = level_for(all_xp.get(uid, xp))
        return {"rank": rank_of(xp), "name": name, "xp": xp, "level": level, "level_name": level_name(level), "is_you": uid == user.id}

    entries = [entry(uid, xp) for uid, xp in visible[:LEADERBOARD_SIZE]]
    me = ensure_profile(db, user)
    db.commit()
    my_xp = totals.get(user.id, 0)
    my_level = level_for(all_xp.get(user.id, total_xp(db, user.id)))
    you = {
        "rank": rank_of(my_xp) if my_xp > 0 else None,
        "xp": my_xp,
        "name": public_name(me, user),
        "level": my_level,
        "level_name": level_name(my_level),
        "visibility": me.visibility,
        "in_top": any(e["is_you"] for e in entries),
    }
    out = {"period": period, "entries": entries, "you": you, "ranked": len(visible)}
    if start is not None:
        out["week_start"] = start
        out["week_end"] = start + timedelta(days=7)
    return out


def _all_time(db: Session, user_ids: list[int]) -> dict[int, int]:
    if not user_ids:
        return {}
    rows = (
        db.query(XpEvent.user_id, func.sum(XpEvent.amount))
        .filter(XpEvent.user_id.in_(user_ids))
        .group_by(XpEvent.user_id)
        .all()
    )
    return {uid: int(xp or 0) for uid, xp in rows}
