"""Admin dashboard API.

Every route needs a signed-in learner (401 otherwise) whose sign-in identity is listed in
ADMIN_IDENTITIES (403 otherwise). Every change is written to the audit log.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import Difficulty, FeedbackModeration, Question, SkillDomain, User, UserFeedback
from app.services import admin as svc
from app.services import purge, question_edits

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_user(user: User = Depends(get_current_user)) -> User:
    if not svc.is_admin(user):
        raise HTTPException(status_code=403, detail="Admins only.")
    return user


Admin = Depends(require_admin_user)


@router.get("/me")
def me(admin: User = Admin) -> dict:
    return {"is_admin": True, "name": admin.display_name, "identity": svc.identity(admin)}


@router.get("/overview")
def overview(days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db), admin: User = Admin) -> dict:
    return svc.overview(db, days=days)


# ----------------------------------------------------------------------------- learners

@router.get("/learners")
def learners(q: str = Query("", max_length=80), sort: str = Query("recent", pattern="^(recent|xp|attempts|joined|name)$"),
             page: int = Query(1, ge=1, le=10000), db: Session = Depends(get_db), admin: User = Admin) -> dict:
    return svc.learners(db, q=q, sort=sort, page=page)


def _learner(db: Session, user_id: int) -> User:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="No such learner.")
    return u


class BoardBody(BaseModel):
    hidden: bool


@router.post("/learners/{user_id}/board")
def learner_board(user_id: int, body: BoardBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    u = _learner(db, user_id)
    if svc.set_board_hidden(db, u, body.hidden):
        svc.audit(db, admin, "learner.board_hidden" if body.hidden else "learner.board_shown", svc.learner_label(db, u))
    db.commit()
    return svc.learner_row(db, user_id)


class ConfirmBody(BaseModel):
    confirm: str = Field(default="", max_length=60)


def _check_confirm(db: Session, u: User, admin: User, body: ConfirmBody) -> None:
    if u.id == admin.id:
        raise HTTPException(status_code=400, detail="You can't do this to your own account here.")
    want = svc.confirm_word(db, u)
    if body.confirm.strip().lstrip("@").lower() != want.lower():
        raise HTTPException(status_code=400, detail=f"Type {want} to confirm.")


@router.post("/learners/{user_id}/reset-xp")
def learner_reset_xp(user_id: int, body: ConfirmBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    u = _learner(db, user_id)
    _check_confirm(db, u, admin, body)
    before = svc.reset_xp(db, u)
    svc.audit(db, admin, "learner.xp_reset", svc.learner_label(db, u), previous_xp=before)
    db.commit()
    return svc.learner_row(db, user_id)


@router.post("/learners/{user_id}/delete")
def learner_delete(user_id: int, body: ConfirmBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    u = _learner(db, user_id)
    _check_confirm(db, u, admin, body)
    label = svc.learner_label(db, u)
    removed = purge.purge(db, u, commit=False)
    svc.audit(db, admin, "learner.deleted", label, removed={k: v for k, v in removed.items() if v})
    db.commit()
    return {"deleted": True, "removed": removed}


# ----------------------------------------------------------------------------- questions

@router.get("/questions")
def questions(topic: str = Query("", max_length=40), language: str = Query("", max_length=32),
              difficulty: str = Query("", max_length=20), kind: str = Query("", max_length=20),
              status: str = Query("", pattern="^(|visible|hidden|edited|new)$"), q: str = Query("", max_length=80),
              sort: str = Query("id", pattern="^(id|attempts|pass_rate|fail_rate|rating)$"),
              page: int = Query(1, ge=1, le=10000), db: Session = Depends(get_db), admin: User = Admin) -> dict:
    return svc.questions(db, topic=topic, language=language, difficulty=difficulty, kind=kind, status=status,
                         q=q, sort=sort, page=page)


@router.get("/questions/{qid}")
def question(qid: int, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    d = svc.question_detail(db, qid)
    if d is None:
        raise HTTPException(status_code=404, detail="No such question.")
    return d


class QuestionEditBody(BaseModel):
    question_text: str | None = Field(default=None, max_length=question_edits.MAX_TEXT)
    reference_answer: str | None = Field(default=None, max_length=question_edits.MAX_TEXT)
    key_idea: str | None = Field(default=None, max_length=question_edits.MAX_TEXT)
    check_only: bool = False


@router.post("/questions/{qid}")
def question_edit(qid: int, body: QuestionEditBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    q = db.get(Question, qid)
    if q is None:
        raise HTTPException(status_code=404, detail="No such question.")
    if body.question_text is not None and not body.question_text.strip():
        raise HTTPException(status_code=422, detail="The question can't be empty.")
    if body.reference_answer is not None and not body.reference_answer.strip():
        raise HTTPException(status_code=422, detail="The model answer can't be empty.")
    notes = question_edits.style_notes(body.question_text, body.key_idea, body.reference_answer)
    if body.check_only:
        return {"saved": False, "notes": notes}
    changes = question_edits.edit(db, q, question_text=body.question_text,
                                  reference_answer=body.reference_answer, key_idea=body.key_idea)
    if changes:
        svc.audit(db, admin, "question.edited", f"question #{q.id}: {q.title}",
                  fields=sorted(changes), before={k: v[0][:300] for k, v in changes.items()})
    db.commit()
    return {"saved": bool(changes), "notes": notes, "question": svc.question_detail(db, qid)}


@router.post("/questions/{qid}/visibility")
def question_visibility(qid: int, body: BoardBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    q = db.get(Question, qid)
    if q is None:
        raise HTTPException(status_code=404, detail="No such question.")
    if question_edits.set_hidden(db, q, body.hidden):
        svc.audit(db, admin, "question.hidden" if body.hidden else "question.shown", f"question #{q.id}: {q.title}")
    db.commit()
    return svc.question_detail(db, qid)


class NewQuestionBody(BaseModel):
    topic: str = Field(max_length=40)
    language: str = Field(max_length=32)
    difficulty: str = Field(pattern="^(beginner|intermediate|advanced)$")
    title: str = Field(min_length=3, max_length=120)
    code: str = Field(default="", max_length=4000)
    question_text: str = Field(min_length=10, max_length=question_edits.MAX_TEXT)
    key_points: str = Field(min_length=3, max_length=1500)
    reference_answer: str = Field(min_length=10, max_length=question_edits.MAX_TEXT)
    key_idea: str = Field(default="", max_length=question_edits.MAX_TEXT)
    check_only: bool = False


@router.post("/questions")
def question_create(body: NewQuestionBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    domain = db.query(SkillDomain).filter_by(slug=body.topic).first()
    if domain is None:
        raise HTTPException(status_code=422, detail="Unknown topic.")
    if body.language not in svc.LANGUAGE_LABELS:
        raise HTTPException(status_code=422, detail="Unknown language.")
    if db.query(Question).filter_by(title=body.title.strip(), language=body.language).first():
        raise HTTPException(status_code=409, detail="A question with that title already exists for this language.")
    notes = question_edits.style_notes(body.question_text, body.key_idea, body.reference_answer)
    if body.check_only:
        return {"saved": False, "notes": notes}
    try:
        q = question_edits.create(db, domain=domain, difficulty=Difficulty(body.difficulty).value, language=body.language,
                                  title=body.title, code=body.code, question_text=body.question_text,
                                  key_points=body.key_points, reference_answer=body.reference_answer,
                                  key_idea=body.key_idea)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    svc.audit(db, admin, "question.created", f"question #{q.id}: {q.title}")
    db.commit()
    return {"saved": True, "notes": notes, "question": svc.question_detail(db, q.id)}


@router.get("/exercises")
def exercises(db: Session = Depends(get_db), admin: User = Admin) -> dict:
    return {"items": svc.exercises(db)}


# ----------------------------------------------------------------------------- feedback

@router.get("/feedback")
def feedback(status: str = Query("", pattern="^(|new|reviewed|hidden)$"), category: str = Query("", max_length=32),
             rating: int | None = Query(None, ge=1, le=5), q: str = Query("", max_length=80),
             page: int = Query(1, ge=1, le=10000), db: Session = Depends(get_db), admin: User = Admin) -> dict:
    return svc.feedback(db, status=status, category=category, rating=rating, q=q, page=page)


def _fb(db: Session, fid: int) -> UserFeedback:
    f = db.get(UserFeedback, fid)
    if f is None:
        raise HTTPException(status_code=404, detail="No such feedback.")
    return f


class ReviewBody(BaseModel):
    reviewed: bool


@router.post("/feedback/{fid}/review")
def feedback_review(fid: int, body: ReviewBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    from datetime import datetime, timezone

    f = _fb(db, fid)
    m = svc.moderation(db, f)
    if bool(m.reviewed_at) != body.reviewed:
        m.reviewed_at = datetime.now(timezone.utc) if body.reviewed else None
        svc.audit(db, admin, "feedback.reviewed" if body.reviewed else "feedback.unreviewed", f"feedback #{f.id}")
    db.commit()
    return {"id": f.id, "reviewed": body.reviewed}


@router.post("/feedback/{fid}/visibility")
def feedback_visibility(fid: int, body: BoardBody, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    f = _fb(db, fid)
    m = svc.moderation(db, f)
    if bool(m.hidden) != body.hidden:
        m.hidden = 1 if body.hidden else 0
        svc.audit(db, admin, "feedback.hidden" if body.hidden else "feedback.shown", f"feedback #{f.id}")
    db.commit()
    return {"id": f.id, "hidden": body.hidden}


@router.post("/feedback/{fid}/delete")
def feedback_delete(fid: int, db: Session = Depends(get_db), admin: User = Admin) -> dict:
    f = _fb(db, fid)
    db.query(FeedbackModeration).filter(FeedbackModeration.feedback_id == f.id).delete()
    svc.audit(db, admin, "feedback.deleted", f"feedback #{f.id}", rating=f.rating, category=f.category,
              excerpt=f.message[:120])
    db.delete(f)
    db.commit()
    return {"deleted": True}


# ----------------------------------------------------------------------------- audit

@router.get("/audit")
def audit(action: str = Query("", max_length=40), page: int = Query(1, ge=1, le=10000),
          db: Session = Depends(get_db), admin: User = Admin) -> dict:
    return svc.audit_page(db, action=action, page=page)
