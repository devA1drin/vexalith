"""Adaptive next-question endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import QuestionOut
from app.services.learning import get_next_question

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/next", response_model=QuestionOut)
def next_question(
    user_id: int = Query(..., description="Learner user id"),
    db: Session = Depends(get_db),
) -> QuestionOut:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return get_next_question(db, user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
