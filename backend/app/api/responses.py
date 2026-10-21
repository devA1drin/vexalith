"""Submit answer → receive feedback."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Question, User
from app.schemas.schemas import ResponseCreate, ResponseOut, FeedbackPayload
from app.services.learning import submit_response

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("", response_model=ResponseOut, status_code=201)
def create_response(body: ResponseCreate, db: Session = Depends(get_db)) -> ResponseOut:
    user = db.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    question = db.get(Question, body.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    response, payload = submit_response(
        db, user=user, question=question, answer_text=body.answer_text
    )
    return ResponseOut(
        id=response.id,
        user_id=response.user_id,
        question_id=response.question_id,
        answer_text=response.answer_text,
        created_at=response.created_at,
        feedback=payload,
    )
