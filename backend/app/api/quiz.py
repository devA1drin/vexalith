"""Timed quizzes for the signed-in learner: options, start, the live state, answers, results, history."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.services import quiz

router = APIRouter(prefix="/quiz", tags=["quiz"])


class StartIn(BaseModel):
    scope: str = Field(pattern=r"^(topic|language|path|mixed)$")
    value: str = Field("", max_length=64, pattern=r"^[a-z0-9_-]*$")
    length: int
    minutes: int
    instant: bool = False


class AnswerIn(BaseModel):
    position: int = Field(ge=0, le=99)
    answer_text: str = Field(max_length=4000)


class SkipIn(BaseModel):
    position: int = Field(ge=0, le=99)


def _fail(e: quiz.QuizError):
    if e.quiz_id is not None:
        return JSONResponse(status_code=e.status, content={"detail": e.detail, "quiz_id": e.quiz_id})
    raise HTTPException(status_code=e.status, detail=e.detail)


@router.get("/options")
def options(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return jsonable_encoder(quiz.options(db, user))


@router.get("/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return jsonable_encoder(quiz.history(db, user))


@router.post("", status_code=201)
def start(body: StartIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        q = quiz.start(db, user, scope=body.scope, value=body.value, length=body.length,
                       minutes=body.minutes, instant=body.instant)
    except quiz.QuizError as e:
        return _fail(e)
    return jsonable_encoder(quiz.state(db, user, q))


@router.get("/{quiz_id}")
def get_state(quiz_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        q = quiz.get(db, user, quiz_id)
    except quiz.QuizError as e:
        return _fail(e)
    return jsonable_encoder(quiz.state(db, user, q))


@router.post("/{quiz_id}/answer")
def answer(quiz_id: int, body: AnswerIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return jsonable_encoder(quiz.answer(db, user, quiz_id, body.position, body.answer_text))
    except quiz.QuizError as e:
        return _fail(e)


@router.post("/{quiz_id}/skip")
def skip(quiz_id: int, body: SkipIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return jsonable_encoder(quiz.skip(db, user, quiz_id, body.position))
    except quiz.QuizError as e:
        return _fail(e)


@router.post("/{quiz_id}/finish")
def finish(quiz_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        q = quiz.get(db, user, quiz_id)
        quiz.finish(db, user, q, ended_by="ended")
        return jsonable_encoder(quiz.results(db, user, quiz_id))
    except quiz.QuizError as e:
        return _fail(e)


@router.get("/{quiz_id}/results")
def results(quiz_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return jsonable_encoder(quiz.results(db, user, quiz_id))
    except quiz.QuizError as e:
        return _fail(e)
