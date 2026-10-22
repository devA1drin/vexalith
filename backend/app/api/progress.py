"""Progress dashboard data for the signed-in learner."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import ProgressOut, RecommendationsOut
from app.services.learning import get_progress
from app.services.recommendations import get_recommendations

router = APIRouter(tags=["progress"])


@router.get("/progress", response_model=ProgressOut)
def progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProgressOut:
    return get_progress(db, user)


@router.get("/recommendations", response_model=RecommendationsOut)
def recommendations(
    language: Literal["python", "javascript", "php", "cpp", "html", "css", "general"] | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationsOut:
    """Weakest skills, languages to revisit and a few unseen next questions."""
    return get_recommendations(db, user, language=language)
