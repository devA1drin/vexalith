"""Learning paths for the signed-in learner: overview, one path, a step's next question, skip ahead."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import QuestionOut
from app.services import paths

router = APIRouter(prefix="/paths", tags=["paths"])


def _path(slug: str):
    p = paths.get_path(slug)
    if p is None:
        raise HTTPException(status_code=404, detail="No such path")
    return p


def _step(p, number: int):
    if not 1 <= number <= len(p.steps):
        raise HTTPException(status_code=404, detail="No such step")
    return p.steps[number - 1]


def _ids(raw: str | None) -> set[int]:
    return {int(x) for x in (raw or "").split(",") if x.strip().isdigit()}


@router.get("")
def overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Every path with progress, plus where to continue."""
    return paths.overview(db, user)


@router.get("/{slug}")
def detail(slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """One path with each step's state (locked, open or done) and progress."""
    _path(slug)
    return paths.detail(db, user, slug)


@router.get("/{slug}/steps/{number}/next", response_model=QuestionOut)
def next_question(
    slug: str,
    number: int,
    exclude: str | None = Query(None, description="Comma-separated question ids to avoid"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuestionOut:
    """The next question for a step; answer it with POST /responses like any other question."""
    p = _path(slug)
    _step(p, number)
    q = paths.next_question(db, user, p, number, _ids(exclude))
    if q is None:
        raise HTTPException(status_code=404, detail="This step has no questions")
    return q


@router.post("/{slug}/steps/{number}/skip-ahead")
def skip_ahead(slug: str, number: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Open a locked step early. It's remembered, and the step says so."""
    p = _path(slug)
    step = _step(p, number)
    paths.skip_ahead(db, user, p.slug, step.key)
    return paths.detail(db, user, slug)
