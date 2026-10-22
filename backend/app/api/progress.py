"""Progress dashboard data for the signed-in learner."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import ProgressOut
from app.services.learning import get_progress

router = APIRouter(tags=["progress"])


@router.get("/progress", response_model=ProgressOut)
def progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProgressOut:
    return get_progress(db, user)
