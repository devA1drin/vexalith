"""Submit an explanation → receive explainable feedback."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import Question, User
from app.schemas.schemas import ResponseCreate, ResponseOut
from app.services.learning import submit_response

MIN_EXPLANATION_CHARS = 10

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("", response_model=ResponseOut, status_code=201)
def create_response(
    body: ResponseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResponseOut:
    question = db.get(Question, body.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    min_len = 1 if (question.rubric or {}).get("kind") == "fill_blank" else MIN_EXPLANATION_CHARS
    if len(body.answer_text.strip()) < min_len:
        raise HTTPException(status_code=422, detail=f"Answer must be at least {min_len} characters")
    response, payload = submit_response(db, user=user, question=question, answer_text=body.answer_text)
    return ResponseOut(
        id=response.id,
        question_id=response.question_id,
        answer_text=response.answer_text,
        created_at=response.created_at,
        feedback=payload,
    )
