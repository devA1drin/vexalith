"""Progress dashboard data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import ProgressOut
from app.services.learning import get_progress

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{user_id}", response_model=ProgressOut)
def progress(user_id: int, db: Session = Depends(get_db)) -> ProgressOut:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_progress(db, user)
