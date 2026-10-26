"""Mistake review for the signed-in learner: the list (with filters) and exercise retries."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.content.exercises import BY_SLUG as EXERCISES
from app.db.session import get_db
from app.models.models import Question, User
from app.services import quiz, review

router = APIRouter(prefix="/review", tags=["review"])

SLUG = r"^[a-z0-9_-]*$"


@router.get("")
def review_list(
    topic: str = Query("", max_length=64, pattern=SLUG),
    language: str = Query("", max_length=32, pattern=SLUG),
    path: str = Query("", max_length=40, pattern=SLUG),
    difficulty: str = Query("", pattern=r"^(|beginner|intermediate|advanced)$"),
    kind: str = Query("", pattern=r"^(|question|exercise)$"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> dict:
    quiz.close_expired(db, user)  # a quiz that ran out of time feeds its missed questions in
    return jsonable_encoder(review.page(db, user, topic=topic, language=language, path=path,
                                        difficulty=difficulty, kind=kind))


@router.post("/questions/{question_id}/retry", status_code=201)
def retry_question(question_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if db.get(Question, question_id) is None:
        raise HTTPException(status_code=404, detail="Question not found")
    review.mark_retry(db, user, f"q:{question_id}")
    return {"ok": True}


@router.post("/exercises/{slug}/retry", status_code=201)
def retry_exercise(slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if slug not in EXERCISES:
        raise HTTPException(status_code=404, detail="No such exercise")
    review.mark_retry(db, user, f"x:{slug}")
    return {"ok": True}
