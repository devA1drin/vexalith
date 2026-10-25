"""Browser coding exercises.

Learner code is NEVER executed on the server. The browser runs it (Pyodide /
a locked-down Web Worker) against the test inputs and posts the outputs back;
the server only compares those outputs with expected values. Expected values of
hidden tests never leave the server.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.content.exercise_guides import commented_solution, explanation_for, hints_for
from app.content.exercises import BY_SLUG, COMING_SOON_LANGUAGES, EXERCISES, RUNNABLE_LANGUAGES
from app.db.session import get_db
from app.models.models import ExerciseAttempt, ExerciseHelp, User

router = APIRouter(prefix="/exercises", tags=["exercises"])


def _norm(value: Any) -> Any:
    # 3.0 and 3 are the same answer (PHP and C++ sometimes print whole numbers as floats).
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [_norm(v) for v in value]
    if isinstance(value, dict):
        return {k: _norm(v) for k, v in value.items()}
    return value


def canonical(value: Any) -> str:
    return json.dumps(_norm(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def same(output: str | None, expected: Any) -> bool:
    if output is None:
        return False
    try:
        return canonical(json.loads(output)) == canonical(expected)
    except (ValueError, TypeError):
        return False


def _best(db: Session, user: User) -> dict[str, tuple[int, int]]:
    rows = (
        db.query(ExerciseAttempt.slug, func.max(ExerciseAttempt.passed), func.max(ExerciseAttempt.total))
        .filter(ExerciseAttempt.user_id == user.id)
        .group_by(ExerciseAttempt.slug)
        .all()
    )
    return {slug: (int(p or 0), int(t or 0)) for slug, p, t in rows}


def solved_slugs(db: Session, user: User) -> set[str]:
    return {slug for slug, (p, t) in _best(db, user).items() if t and slug in BY_SLUG and p >= len(BY_SLUG[slug]["tests"])}


def _help_rows(db: Session, user: User, slug: str | None = None) -> list[ExerciseHelp]:
    q = db.query(ExerciseHelp).filter(ExerciseHelp.user_id == user.id)
    if slug:
        q = q.filter(ExerciseHelp.slug == slug)
    return q.all()


def _with_help(db: Session, user: User) -> set[str]:
    """Exercises whose solution was revealed before the learner passed them."""
    return {h.slug for h in _help_rows(db, user) if h.kind == "solution" and h.before_pass}


def _help(db: Session, user: User, e: dict, solved: bool) -> dict:
    """The "How to solve it" state. The explanation and the solution stay hidden until the
    learner passes every test or chooses to reveal the solution."""
    rows = _help_rows(db, user, e["slug"])
    hints = hints_for(e["slug"], e["language"])
    shown = min(len(hints), max((h.level for h in rows if h.kind == "hint"), default=0))
    revealed = next((h for h in rows if h.kind == "solution"), None)
    unlocked = solved or revealed is not None
    return {
        "hint_count": len(hints),
        "hints": hints[:shown],
        "solution_revealed": revealed is not None,
        "solved_with_help": bool(revealed and revealed.before_pass),
        "explanation": explanation_for(e["slug"], e["language"]) if unlocked else None,
        "solution": commented_solution(e["slug"], e["language"], e["solution"]) if unlocked else None,
    }


@router.get("")
def list_exercises(
    language: str | None = Query(None, pattern=r"^[a-z]{2,12}$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    best = _best(db, user)
    helped = _with_help(db, user)
    items = []
    for e in EXERCISES:
        if language and e["language"] != language:
            continue
        p, _ = best.get(e["slug"], (0, 0))
        n = len(e["tests"])
        items.append({
            "slug": e["slug"], "title": e["title"], "language": e["language"], "difficulty": e["difficulty"],
            "topic": e["topic"], "tests": n, "best_passed": p, "solved": p >= n, "attempted": e["slug"] in best,
            "solved_with_help": p >= n and e["slug"] in helped,
        })
    return {"exercises": items, "runnable_languages": list(RUNNABLE_LANGUAGES), "coming_soon": list(COMING_SOON_LANGUAGES)}


@router.get("/{slug}")
def get_exercise(slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    e = BY_SLUG.get(slug)
    if not e:
        raise HTTPException(status_code=404, detail="Exercise not found")
    v = e["visible"]
    best = _best(db, user)
    p, _ = best.get(slug, (0, 0))
    solved = p >= len(e["tests"])
    return {
        "slug": e["slug"], "title": e["title"], "language": e["language"], "difficulty": e["difficulty"],
        "topic": e["topic"], "description": e["description"],
        "function": e["function"], "starter": e["starter"], "signature": e.get("signature"),
        "timeout_ms": e["timeout_ms"],
        "visible_tests": [{"args": t["args"], "expected": t["expected"]} for t in e["tests"][:v]],
        # Hidden tests: only the inputs. Their expected values stay on the server.
        "hidden_tests": [{"args": t["args"]} for t in e["tests"][v:]],
        "best_passed": p, "solved": solved, "attempted": slug in best,
        "help": _help(db, user, e, solved),
    }


class RunResult(BaseModel):
    output: str | None = Field(default=None, max_length=4000)  # JSON of the return value
    error: str | None = Field(default=None, max_length=1000)


class SubmitIn(BaseModel):
    code: str = Field(min_length=1, max_length=10000)
    results: list[RunResult] = Field(max_length=50)


@router.post("/{slug}/submit")
def submit(slug: str, body: SubmitIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    e = BY_SLUG.get(slug)
    if not e:
        raise HTTPException(status_code=404, detail="Exercise not found")
    tests = e["tests"]
    if len(body.results) != len(tests):
        raise HTTPException(status_code=422, detail=f"Expected {len(tests)} results")
    checks = []
    for i, (t, r) in enumerate(zip(tests, body.results)):
        ok = r.error is None and same(r.output, t["expected"])
        visible = i < e["visible"]
        checks.append({"index": i, "visible": visible, "passed": ok, **({"expected": t["expected"]} if visible else {})})
    passed = sum(c["passed"] for c in checks)
    was_solved = slug in solved_slugs(db, user)
    db.add(ExerciseAttempt(user_id=user.id, slug=slug, language=e["language"], passed=passed, total=len(tests), code=body.code))
    db.commit()
    solved = passed == len(tests)
    return {
        "slug": slug, "passed": passed, "total": len(tests), "solved": solved,
        # After a pass the explanation and reference solution are shown for comparison.
        "help": _help(db, user, e, solved or was_solved),
        "first_solve": solved and not was_solved, "checks": checks,
        "message": (
            "All tests passed. Nice work!" if solved
            else "Check the failing tests below and try again. You're getting there."
        ),
    }


def _save(db: Session, row: ExerciseHelp) -> None:
    # A double click can try to store the same hint twice; the unique constraint keeps one.
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def _exercise_or_404(slug: str) -> dict:
    e = BY_SLUG.get(slug)
    if not e:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return e


@router.post("/{slug}/hints")
def reveal_hint(slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Reveal the next hint level (one at a time)."""
    e = _exercise_or_404(slug)
    solved = slug in solved_slugs(db, user)
    shown = len(_help(db, user, e, solved)["hints"])
    if shown < len(hints_for(slug, e["language"])):
        _save(db, ExerciseHelp(user_id=user.id, slug=slug, kind="hint", level=shown + 1, before_pass=0 if solved else 1))
    return _help(db, user, e, solved)


class RevealIn(BaseModel):
    confirm: bool = False


@router.post("/{slug}/solution")
def reveal_solution(slug: str, body: RevealIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Show the reference solution and explanation.

    Before the first attempt the learner has to confirm ("Are you sure?"). Revealing it
    before passing marks the exercise as solved with help.
    """
    e = _exercise_or_404(slug)
    best = _best(db, user)
    solved = slug in solved_slugs(db, user)
    if not body.confirm and slug not in best and not solved:
        raise HTTPException(status_code=409, detail="Try running your code first, or confirm that you want to see the solution.")
    if not any(h.kind == "solution" for h in _help_rows(db, user, slug)):
        _save(db, ExerciseHelp(user_id=user.id, slug=slug, kind="solution", level=0, before_pass=0 if solved else 1))
    return _help(db, user, e, solved)
