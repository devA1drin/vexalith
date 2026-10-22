"""Current-user endpoint (identity comes from the verified backend JWT)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import UserOut
from app.services.learning import ensure_user_masteries

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    ensure_user_masteries(db, user)
    return user
