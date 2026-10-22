"""Product feedback endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import PublicFeedbackOut, UserFeedbackCreate, UserFeedbackOut
from app.services import user_feedback as svc

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=UserFeedbackOut, status_code=201)
def submit(body: UserFeedbackCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return svc.to_out(svc.create_feedback(db, user=user, body=body))


@router.get("/mine", response_model=list[UserFeedbackOut])
def mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return svc.list_mine(db, user)


@router.get("/recent", response_model=list[PublicFeedbackOut])
def recent(limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    return svc.list_recent_public(db, limit=limit)
