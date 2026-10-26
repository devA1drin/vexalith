"""The signed-in learner's profile: read and edit it, check a handle, and a read-only summary."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.services import profile

router = APIRouter(prefix="/profile", tags=["profile"])


class QuizDefaultsIn(BaseModel):
    scope: Literal["topic", "language", "path", "mixed"]
    value: str = Field("", max_length=64, pattern=r"^[a-z0-9_-]*$")
    length: int = Field(ge=1, le=100)
    minutes: int = Field(ge=1, le=60)
    instant: bool = False


class ProfileIn(BaseModel):
    """Every field is optional: only what's sent is changed. ``quiz_defaults: null`` clears them."""

    display_name: str | None = Field(None, max_length=200)
    handle: str | None = Field(None, max_length=200)
    visibility: Literal["handle", "name", "anonymous", "hidden"] | None = None
    avatar: str | None = Field(None, max_length=32)
    bio: str | None = Field(None, max_length=1000)
    practice_languages: list[str] | None = Field(None, max_length=8)
    answer_language: Literal["en", "fil", "taglish"] | None = None
    quiz_defaults: QuizDefaultsIn | None = None


@router.get("")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return jsonable_encoder(profile.profile_out(db, user))


@router.put("")
def put_profile(body: ProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    if "quiz_defaults" in data and data["quiz_defaults"] is None:
        data["quiz_defaults"] = {}
    try:
        return jsonable_encoder(profile.update(db, user, data))
    except profile.ProfileError as e:
        return JSONResponse(status_code=422, content={"detail": e.message, "field": e.field})


@router.get("/handle")
def check_handle(handle: str = Query(..., max_length=200), user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)) -> dict:
    """Is this handle free and allowed? (Saving checks again.)"""
    return profile.check_handle(db, user, handle)


@router.get("/summary")
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return jsonable_encoder(profile.summary(db, user))
