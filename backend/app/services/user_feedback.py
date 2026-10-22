"""Product feedback: validation, spam protection, listing."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import User, UserFeedback
from app.schemas.schemas import PublicFeedbackOut, UserFeedbackCreate, UserFeedbackOut

URL_RE = re.compile(r"https?://|www\.", re.I)
MAX_LINKS = 2
DUPLICATE_WINDOW = timedelta(hours=24)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def create_feedback(db: Session, *, user: User, body: UserFeedbackCreate, now: datetime | None = None) -> UserFeedback:
    settings = get_settings()
    now = now or datetime.now(timezone.utc)

    if len(URL_RE.findall(body.message)) > MAX_LINKS:
        raise HTTPException(status_code=422, detail="Too many links in the message.")
    if re.search(r"(.)\1{24,}", body.message):
        raise HTTPException(status_code=422, detail="Message looks like spam (repeated characters).")

    recent = (
        db.query(UserFeedback)
        .filter(UserFeedback.user_id == user.id, UserFeedback.created_at >= now - timedelta(days=1))
        .all()
    )
    last_hour = [f for f in recent if _aware(f.created_at) >= now - timedelta(hours=1)]
    if len(last_hour) >= settings.feedback_max_per_hour or len(recent) >= settings.feedback_max_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit: at most {settings.feedback_max_per_hour} submissions per hour "
            f"and {settings.feedback_max_per_day} per day.",
            headers={"Retry-After": "3600"},
        )
    normalized = " ".join(body.message.lower().split())
    for f in recent:
        if _aware(f.created_at) >= now - DUPLICATE_WINDOW and " ".join(f.message.lower().split()) == normalized:
            raise HTTPException(status_code=409, detail="You already submitted this exact feedback.")

    fb = UserFeedback(
        user_id=user.id,
        rating=body.rating,
        category=body.category,
        message=body.message,
        page_context=body.page_context,
        created_at=now,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


def to_out(fb: UserFeedback) -> UserFeedbackOut:
    return UserFeedbackOut(
        id=fb.id, rating=fb.rating, category=fb.category, message=fb.message,
        page_context=fb.page_context, created_at=fb.created_at,
    )


def list_mine(db: Session, user: User, limit: int = 50) -> list[UserFeedbackOut]:
    rows = (
        db.query(UserFeedback).filter_by(user_id=user.id)
        .order_by(UserFeedback.created_at.desc()).limit(limit).all()
    )
    return [to_out(r) for r in rows]


def list_recent_public(db: Session, limit: int = 20) -> list[PublicFeedbackOut]:
    rows = (
        db.query(UserFeedback, User)
        .join(User, User.id == UserFeedback.user_id)
        .order_by(UserFeedback.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        PublicFeedbackOut(
            id=f.id,
            author_name=u.display_name,
            author_avatar_url=u.avatar_url,
            rating=f.rating,
            category=f.category,
            message=f.message,
            created_at=f.created_at,
        )
        for f, u in rows
    ]
