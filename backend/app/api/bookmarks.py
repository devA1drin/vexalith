"""Bookmarks for the signed-in learner: the list (with filters), saved keys, and save/unsave."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.content.exercises import BY_SLUG as EXERCISES
from app.db.session import get_db
from app.models.models import Question, User
from app.services import bookmarks

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

SLUG = r"^[a-z0-9_-]*$"


class SaveIn(BaseModel):
    saved: bool = True
    note: str | None = Field(None, max_length=1000)


def _set(db: Session, user: User, key: str, body: SaveIn) -> dict:
    try:
        return bookmarks.set_saved(db, user, key, body.saved, body.note)
    except bookmarks.BookmarkError as e:
        raise HTTPException(status_code=e.status, detail=e.detail) from e


@router.get("")
def bookmark_list(
    kind: str = Query("", pattern=r"^(|question|exercise)$"),
    topic: str = Query("", max_length=64, pattern=SLUG),
    language: str = Query("", max_length=32, pattern=SLUG),
    user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> dict:
    return jsonable_encoder(bookmarks.page(db, user, kind=kind, topic=topic, language=language))


@router.get("/keys")
def bookmark_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Just the saved keys, so any page can show its save buttons in the right state."""
    return {"keys": bookmarks.keys(db, user)}


@router.put("/questions/{question_id}")
def save_question(question_id: int, body: SaveIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if body.saved and db.get(Question, question_id) is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return _set(db, user, f"q:{question_id}", body)


@router.put("/exercises/{slug}")
def save_exercise(slug: str, body: SaveIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if body.saved and slug not in EXERCISES:
        raise HTTPException(status_code=404, detail="No such exercise")
    return _set(db, user, f"x:{slug}", body)
