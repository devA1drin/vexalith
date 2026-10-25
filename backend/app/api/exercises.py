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
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.content.exercises import BY_SLUG, COMING_SOON_LANGUAGES, EXERCISES, RUNNABLE_LANGUAGES
from app.db.session import get_db
from app.models.models import ExerciseAttempt, User

router = APIRouter(prefix="/exercises", tags=["exercises"])


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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


@router.get("")
def list_exercises(
    language: str | None = Query(None, pattern=r"^[a-z]{2,12}$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    best = _best(db, user)
    items = []
    for e in EXERCISES:
        if language and e["language"] != language:
            continue
        p, _ = best.get(e["slug"], (0, 0))
        n = len(e["tests"])
        items.append({
            "slug": e["slug"], "title": e["title"], "language": e["language"], "difficulty": e["difficulty"],
            "topic": e["topic"], "tests": n, "best_passed": p, "solved": p >= n, "attempted": e["slug"] in best,
        })
    return {"exercises": items, "runnable_languages": list(RUNNABLE_LANGUAGES), "coming_soon": list(COMING_SOON_LANGUAGES)}


@router.get("/{slug}")
def get_exercise(slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    e = BY_SLUG.get(slug)
    if not e:
        raise HTTPException(status_code=404, detail="Exercise not found")
    v = e["visible"]
    p, _ = _best(db, user).get(slug, (0, 0))
    return {
        "slug": e["slug"], "title": e["title"], "language": e["language"], "difficulty": e["difficulty"],
        "topic": e["topic"], "description": e["description"], "task": e["task"],
        "function": e["function"], "starter": e["starter"],
        "timeout_ms": e["timeout_ms"],
        "visible_tests": [{"args": t["args"], "expected": t["expected"]} for t in e["tests"][:v]],
        # Hidden tests: only the inputs. Their expected values stay on the server.
        "hidden_tests": [{"args": t["args"]} for t in e["tests"][v:]],
        "best_passed": p, "solved": p >= len(e["tests"]),
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
        "first_solve": solved and not was_solved, "checks": checks,
        "message": (
            "All tests passed. Nice work!" if solved
            else f"{passed} of {len(tests)} tests passed. Check the failing ones and try again, you're getting there."
        ),
    }
