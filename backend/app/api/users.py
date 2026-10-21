"""User create / get endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut
from app.services.learning import ensure_user_masteries

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter_by(display_name=body.display_name).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="display_name already taken")
    user = User(display_name=body.display_name.strip())
    db.add(user)
    db.commit()
    db.refresh(user)
    ensure_user_masteries(db, user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
