"""The learner's profile: chosen name, avatar, bio, preferences and a read-only summary.

Everything here is checked on the server: names and handles are cleaned and validated,
handles are unique (ignoring case), and the email is never returned or shown.
The leaderboard handle and visibility live in LearnerProfile (see services/xp.py),
so the profile edits the same setting the leaderboard uses.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content.domains import LANGUAGES
from app.models.models import Bookmark, LearnerProfile, User, UserSettings
from app.services import xp

NAME_MIN, NAME_MAX = 2, 40
HANDLE_MIN, HANDLE_MAX = 3, 24
BIO_MAX = 160
BIO_LINES = 3
LANGUAGE_SLUGS = [lang["slug"] for lang in LANGUAGES]
ANSWER_LANGUAGES = ("en", "fil", "taglish")
# "photo" is the GitHub/Google picture (only offered when there is one, and never shown on the leaderboard).
AVATARS = xp.AVATAR_MARKS
DEFAULT_AVATAR = "initials-ink"
RESERVED_HANDLES = {"admin", "administrator", "moderator", "mod", "staff", "support", "vexalith", "system", "root", "null"}

_CONTROL = re.compile(r"[\u0000-\u0008\u000b-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
_NAME_OK = re.compile(r"^[^\W_](?:[\w .'\-]*[^\W_])?$")
_HANDLE_OK = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9 ._-]*[A-Za-z0-9])?$")


class ProfileError(ValueError):
    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


def _clean_line(value: str) -> str:
    """NFKC, no control or invisible characters, single spaces."""
    v = unicodedata.normalize("NFKC", value or "")
    v = _CONTROL.sub("", v.replace("\n", " ").replace("\r", " ").replace("\t", " "))
    return re.sub(r"\s+", " ", v).strip()


def _email_part(user: User) -> str:
    return user.email.split("@")[0].strip().lower() if user.email else ""


def clean_name(value: str, user: User) -> str:
    """A display name, or "" to go back to the sign-in name."""
    v = _clean_line(value)
    if not v:
        return ""
    if len(v) < NAME_MIN or len(v) > NAME_MAX:
        raise ProfileError("display_name", f"Use {NAME_MIN} to {NAME_MAX} characters.")
    if "@" in v or "://" in v or not _NAME_OK.match(v):
        raise ProfileError("display_name", "Use letters, numbers, spaces and . ' - only.")
    return v


def clean_handle(value: str, user: User) -> str:
    v = _clean_line(value)
    if len(v) < HANDLE_MIN or len(v) > HANDLE_MAX:
        raise ProfileError("handle", f"Use {HANDLE_MIN} to {HANDLE_MAX} characters.")
    if not _HANDLE_OK.match(v):
        raise ProfileError("handle", "Use letters, numbers, spaces and . _ - only, starting and ending with a letter or number.")
    low = v.lower()
    if low in RESERVED_HANDLES or low.startswith("anonymous"):
        raise ProfileError("handle", "That handle is reserved. Pick another.")
    part = _email_part(user)
    if part and (low == part or low.replace(" ", "") == part.replace(".", "").replace("_", "")):
        raise ProfileError("handle", "Pick a handle that isn't your email address.")
    return v


def handle_taken(db: Session, handle: str, user: User) -> bool:
    row = (
        db.query(LearnerProfile.user_id)
        .filter(func.lower(LearnerProfile.handle) == handle.lower(), LearnerProfile.user_id != user.id)
        .first()
    )
    return row is not None


def check_handle(db: Session, user: User, value: str) -> dict:
    try:
        handle = clean_handle(value, user)
    except ProfileError as e:
        return {"handle": _clean_line(value)[:HANDLE_MAX], "available": False, "reason": e.message}
    if handle_taken(db, handle, user):
        return {"handle": handle, "available": False, "reason": "Someone already has that handle."}
    return {"handle": handle, "available": True, "reason": ""}


def clean_bio(value: str) -> str:
    v = unicodedata.normalize("NFKC", value or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", _CONTROL.sub("", line)).strip() for line in v.split("\n")]
    v = "\n".join(lines).strip()
    v = re.sub(r"\n{2,}", "\n", v)
    if v.count("\n") >= BIO_LINES:
        raise ProfileError("bio", f"Keep it to {BIO_LINES} lines.")
    if len(v) > BIO_MAX:
        raise ProfileError("bio", f"Keep it to {BIO_MAX} characters.")
    if "<" in v or ">" in v:
        raise ProfileError("bio", "Plain text only, without < or >.")
    return v


def clean_languages(values: list[str]) -> list[str]:
    out: list[str] = []
    for v in values:
        if v not in LANGUAGE_SLUGS:
            raise ProfileError("practice_languages", "Unknown language.")
        if v not in out:
            out.append(v)
    return out


def check_quiz_defaults(value: dict | None, opts: dict) -> dict:
    """Checked against what the quiz page offers right now (``opts`` from quiz.options), so a saved
    default always starts."""
    if not value:
        return {}
    scope = value.get("scope")
    choice = "" if scope == "mixed" else str(value.get("value") or "")
    length, minutes = value.get("length"), value.get("minutes")
    if scope not in opts["scopes"] or (scope != "mixed" and choice not in {o["value"] for o in opts["scopes"][scope]}):
        raise ProfileError("quiz_defaults", "Pick a quiz choice from the list.")
    if length not in opts["lengths"] or minutes not in opts["minutes"]:
        raise ProfileError("quiz_defaults", "Pick a length and time from the list.")
    return {"scope": scope, "value": choice, "length": length, "minutes": minutes, "instant": bool(value.get("instant"))}


def get_settings(db: Session, user: User) -> UserSettings:
    """The learner's settings row, created on first use (a lost race reads the other request's row)."""
    row = db.get(UserSettings, user.id)
    if row is not None:
        return row
    db.add(UserSettings(user_id=user.id, practice_languages=[], quiz_defaults={}))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    return db.get(UserSettings, user.id)


def peek_settings(db: Session, user_id: int) -> UserSettings | None:
    """Read-only: the settings row if the learner ever saved one."""
    return db.get(UserSettings, user_id)


def shown_name(user: User, settings: UserSettings | None) -> str:
    """The name the learner chose, else their sign-in name (never an email)."""
    if settings is not None and settings.display_name:
        return settings.display_name
    return xp._safe_name(user) or "Learner"


def chosen_name(settings: UserSettings | None) -> str:
    return settings.display_name if settings is not None else ""


def avatar_of(user: User, settings: UserSettings | None) -> str:
    a = settings.avatar if settings is not None else ""
    if a == "photo":
        return "photo" if user.avatar_url else DEFAULT_AVATAR
    if a in AVATARS:
        return a
    return "photo" if user.avatar_url else DEFAULT_AVATAR


def _iso(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def profile_out(db: Session, user: User) -> dict:
    s = get_settings(db, user)
    p = xp.ensure_profile(db, user)
    db.commit()
    return {
        "display_name": s.display_name,
        "sign_in_name": xp._safe_name(user),
        "leaderboard_avatar": xp.board_avatar(p, s),
        "shown_name": shown_name(user, s),
        "avatar": avatar_of(user, s),
        "avatars": list(AVATARS),
        "photo_url": user.avatar_url,
        "bio": s.bio,
        "practice_languages": list(s.practice_languages or []),
        "answer_language": s.answer_language if s.answer_language in ANSWER_LANGUAGES else "en",
        "quiz_defaults": dict(s.quiz_defaults or {}) or None,
        "handle": p.handle,
        "visibility": p.visibility,
        "leaderboard_name": None if p.visibility == "hidden" else xp.public_name(p, user, s.display_name),
        "provider": user.auth_provider,
        "joined_at": _iso(user.created_at),
        "limits": {"name": [NAME_MIN, NAME_MAX], "handle": [HANDLE_MIN, HANDLE_MAX], "bio": BIO_MAX},
    }


def update(db: Session, user: User, body: dict) -> dict:
    """Apply only the fields that were sent. Raises ProfileError (field + message) on bad input."""
    s = get_settings(db, user)
    p = xp.ensure_profile(db, user)
    if "display_name" in body and body["display_name"] is not None:
        s.display_name = clean_name(body["display_name"], user)
    if "handle" in body and body["handle"] is not None:
        handle = clean_handle(body["handle"], user)
        if handle != p.handle:
            if handle_taken(db, handle, user):
                raise ProfileError("handle", "Someone already has that handle.")
            p.handle = handle
    if body.get("visibility") is not None:
        if body["visibility"] not in xp.VISIBILITY:
            raise ProfileError("visibility", "Pick one of the options.")
        p.visibility = body["visibility"]
    if body.get("avatar") is not None:
        a = body["avatar"]
        if a not in AVATARS and not (a == "photo" and user.avatar_url):
            raise ProfileError("avatar", "Pick one of the marks.")
        s.avatar = a
    if body.get("bio") is not None:
        s.bio = clean_bio(body["bio"])
    if body.get("practice_languages") is not None:
        s.practice_languages = clean_languages(body["practice_languages"])
    if body.get("answer_language") is not None:
        if body["answer_language"] not in ANSWER_LANGUAGES:
            raise ProfileError("answer_language", "Pick English, Filipino or Taglish.")
        s.answer_language = body["answer_language"]
    if "quiz_defaults" in body:
        from app.services import quiz

        s.quiz_defaults = check_quiz_defaults(body["quiz_defaults"], quiz.options(db, user))
    try:
        db.commit()
    except IntegrityError as e:  # two people grabbing the same handle at the same moment
        db.rollback()
        raise ProfileError("handle", "Someone already has that handle.") from e
    return profile_out(db, user)


def summary(db: Session, user: User) -> dict:
    """Read-only numbers for the profile page."""
    from app.services import paths

    xp.sync_user(db, user)
    info = xp.level_info(xp.total_xp(db, user.id))
    badges = xp.badge_list(db, user)
    states = paths.progress(db, user)
    path_rows = [paths.path_out(ps) for ps in states.values()]
    return {
        **info,
        "badges_earned": sum(1 for b in badges if b["earned"]),
        "badges_total": len(badges),
        "paths": [
            {"slug": r["slug"], "name": r["name"], "mark": r["mark"], "steps_done": r["steps_done"],
             "steps_total": r["steps_total"], "progress": r["progress"], "started": r["started"], "finished": r["finished"]}
            for r in path_rows
        ],
        "paths_finished": sum(1 for r in path_rows if r["finished"]),
        "bookmarks": db.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user.id).scalar() or 0,
        "joined_at": _iso(user.created_at),
    }


def quiz_defaults(db: Session, user: User, opts: dict) -> dict | None:
    """Saved quiz defaults for the quiz page, if any (rechecked, so a removed choice is ignored)."""
    s = peek_settings(db, user.id)
    if s is None or not s.quiz_defaults:
        return None
    try:
        return check_quiz_defaults(s.quiz_defaults, opts) or None
    except ProfileError:
        return None
