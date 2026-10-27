"""XP, level, badges and leaderboard for the signed-in learner."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.services import profile, xp

router = APIRouter(tags=["xp"])


@router.get("/xp")
def my_xp(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Level, XP bar, badges (earned and locked) and recent XP."""
    xp.sync_user(db, user)
    return xp.summary(db, user)


@router.post("/xp/sync")
def sync(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Count anything new, then return the level plus what the learner hasn't been told about yet."""
    xp.sync_user(db, user)
    news = xp.news(db, user)
    info = xp.level_info(xp.total_xp(db, user.id))
    return {**info, "news": news}


@router.get("/leaderboard")
def leaderboard(
    period: Literal["week", "all"] = Query("week"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    xp.sync_user(db, user)
    return xp.leaderboard(db, user, period)


class ProfileIn(BaseModel):
    visibility: Literal["handle", "name", "anonymous", "hidden"]


def _profile_out(db: Session, user: User) -> dict:
    p = xp.ensure_profile(db, user)
    db.commit()
    chosen = profile.chosen_name(profile.peek_settings(db, user.id))
    return {
        "visibility": p.visibility,
        "handle": p.handle,
        "shown_as": None if p.visibility == "hidden" else xp.public_name(p, user, chosen),
        # Only offered when it's a real name (never an email).
        "name_available": bool(xp._safe_name(user, chosen)),
        "name": xp._safe_name(user, chosen) or None,
    }


@router.get("/xp/profile")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return _profile_out(db, user)


@router.put("/xp/profile")
def set_profile(body: ProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    p = xp.ensure_profile(db, user)
    p.visibility = body.visibility
    db.commit()
    return _profile_out(db, user)


@router.post("/xp/profile/handle")
def reroll_handle(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Pick a new random handle."""
    p = xp.ensure_profile(db, user)
    p.handle = xp.new_handle(db)
    db.commit()
    return _profile_out(db, user)
