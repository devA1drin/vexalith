"""Learning paths: progress, unlocking, "continue" and the step question picker.

Progress is worked out from the learner's existing history (answers and exercise runs),
so someone who already practised doesn't start at zero. Only two small things are stored:
the step a learner last opened (``path_activity``) and steps they skipped ahead to (``path_skips``).

Rules
-----
- A step's score is the average of the learner's best scores on up to N different questions
  from the step's pool (N is usually 4; questions not answered yet count as 0).
- A step is *done* when that score reaches 75% and, if the step has a coding exercise, it passed.
- The next step *unlocks* when the current one reaches 75% on its questions, or its exercise passed.
- Any locked step can be opened early ("skip ahead"); that's remembered and shown on the step.
- XP: +25 for each step done, +100 for finishing a whole path.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content.exercises import BY_SLUG as EXERCISES
from app.content.paths import ALL_LEVELS, BY_SLUG, PASS_MARK, PATHS, Path, Step, exercise_slugs
from app.models.models import (
    AppMeta,
    ExerciseAttempt,
    Feedback,
    PathActivity,
    PathSkip,
    Question,
    QuestionSkip,
    Response,
    SkillDomain,
    SkillMastery,
    User,
)
from app.services import adaptive

STEP_XP = 25
PATH_XP = 100
LAUNCH_KEY = "paths_launched_at"
LANGUAGE_NAMES = {"python": "Python", "javascript": "JavaScript", "cpp": "C++", "java": "Java", "php": "PHP"}


def _aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _level(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


# ----------------------------------------------------------------------------- pools

def _catalog(db: Session) -> list[tuple[int, str, str, str]]:
    """(id, language, domain slug, level) for every built-in question."""
    rows = (
        db.query(Question.id, Question.language, SkillDomain.slug, Question.difficulty)
        .join(SkillDomain, SkillDomain.id == Question.domain_id)
        .filter(Question.source == "seed")
        .all()
    )
    return [(qid, lang, slug, _level(diff)) for qid, lang, slug, diff in rows]


def pool_ids(step: Step, catalog: list[tuple[int, str, str, str]]) -> list[int]:
    return sorted(
        qid for qid, lang, slug, level in catalog
        if lang in step.languages and slug in step.domains and level in step.levels
    )


# ----------------------------------------------------------------------------- progress

@dataclass
class StepState:
    step: Step
    number: int
    pool: list[int]
    target: int
    best: dict[int, float] = field(default_factory=dict)
    score: float = 0.0
    questions_cleared_at: datetime | None = None
    exercise_slugs: list[str] = field(default_factory=list)
    exercise_passed: str | None = None
    exercise_passed_at: datetime | None = None
    done_at: datetime | None = None
    status: str = "locked"  # locked | open | done
    skipped: bool = False

    @property
    def cleared(self) -> bool:
        """Good enough to unlock the next step."""
        return self.questions_cleared_at is not None or self.exercise_passed_at is not None

    @property
    def answered(self) -> int:
        return min(len(self.best), self.target)


@dataclass
class PathState:
    path: Path
    steps: list[StepState]

    @property
    def done(self) -> int:
        return sum(1 for s in self.steps if s.status == "done")

    @property
    def finished_at(self) -> datetime | None:
        if all(s.done_at for s in self.steps):
            return max(s.done_at for s in self.steps)  # type: ignore[type-var]
        return None

    @property
    def started(self) -> bool:
        return any(s.best or s.exercise_passed for s in self.steps)

    @property
    def current(self) -> StepState:
        """The step to work on next: the first open step that isn't done."""
        for s in self.steps:
            if s.status == "open":
                return s
        for s in self.steps:
            if s.status != "done":
                return s
        return self.steps[-1]

    @property
    def fraction(self) -> float:
        """Overall progress, counting partly finished steps."""
        total = 0.0
        for s in self.steps:
            if s.status == "done":
                total += 1
            else:
                parts = [min(1.0, s.score / PASS_MARK)]
                if s.exercise_slugs:
                    parts.append(1.0 if s.exercise_passed else 0.0)
                total += 0.9 * sum(parts) / len(parts)
        return round(total / len(self.steps), 4)


def _history(db: Session, user: User) -> list[tuple[int, datetime, float]]:
    rows = (
        db.query(Response.question_id, Response.created_at, Feedback.overall_score)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id)
        .order_by(Response.created_at.asc(), Response.id.asc())
        .all()
    )
    return [(qid, _aware(created), float(score or 0.0)) for qid, created, score in rows]


def _passes(db: Session, user: User) -> dict[str, datetime]:
    """First time each exercise passed every test."""
    out: dict[str, datetime] = {}
    rows = (
        db.query(ExerciseAttempt.slug, ExerciseAttempt.passed, ExerciseAttempt.created_at)
        .filter(ExerciseAttempt.user_id == user.id)
        .order_by(ExerciseAttempt.created_at.asc(), ExerciseAttempt.id.asc())
        .all()
    )
    for slug, passed, created in rows:
        e = EXERCISES.get(slug)
        if e and slug not in out and passed >= len(e["tests"]):
            out[slug] = _aware(created)
    return out


def progress(db: Session, user: User, only: str | None = None) -> dict[str, PathState]:
    """Every path's progress for this learner (or just one path with ``only``)."""
    catalog = _catalog(db)
    history = _history(db, user)
    passes = _passes(db, user)
    skips = {(p, s) for p, s in db.query(PathSkip.path, PathSkip.step).filter(PathSkip.user_id == user.id).all()}
    out: dict[str, PathState] = {}
    for path in PATHS:
        if only and path.slug != only:
            continue
        states: list[StepState] = []
        for i, step in enumerate(path.steps):
            pool = pool_ids(step, catalog)
            st = StepState(step=step, number=i + 1, pool=pool, target=max(1, min(step.questions, len(pool))))
            members = set(pool)
            for qid, when, score in history:
                if qid not in members or score <= st.best.get(qid, -1.0):
                    continue
                st.best[qid] = score
                st.score = sum(sorted(st.best.values(), reverse=True)[: st.target]) / st.target
                if st.questions_cleared_at is None and st.score >= PASS_MARK - 1e-9:
                    st.questions_cleared_at = when
            st.score = round(st.score, 4)
            st.exercise_slugs = exercise_slugs(step.exercise)
            passed = sorted((passes[s], s) for s in st.exercise_slugs if s in passes)
            if passed:
                st.exercise_passed_at, st.exercise_passed = passed[0]
            if st.questions_cleared_at and (not st.exercise_slugs or st.exercise_passed_at):
                st.done_at = max(st.questions_cleared_at, st.exercise_passed_at or st.questions_cleared_at)
            unlocked = i == 0 or states[-1].cleared
            st.skipped = (path.slug, step.key) in skips and not unlocked
            st.status = "done" if st.done_at else ("open" if unlocked or st.skipped else "locked")
            states.append(st)
        out[path.slug] = PathState(path, states)
    return out


# ----------------------------------------------------------------------------- XP hook

def awards(db: Session, user: User) -> tuple[dict[str, tuple[str, int, str, datetime]], dict[str, datetime]]:
    """XP events and badges earned by paths (used by ``xp.compute``)."""
    events: dict[str, tuple[str, int, str, datetime]] = {}
    badges: dict[str, datetime] = {}
    finished: list[datetime] = []
    step_times: list[datetime] = []
    for slug, ps in progress(db, user).items():
        for st in ps.steps:
            if st.done_at:
                events[f"path-step:{slug}:{st.step.key}"] = (
                    "path_step", STEP_XP, f"Step done: {ps.path.name}, {st.step.title}", st.done_at)
                step_times.append(st.done_at)
        if ps.finished_at:
            events[f"path:{slug}"] = ("path", PATH_XP, f"Path finished: {ps.path.name}", ps.finished_at)
            finished.append(ps.finished_at)
    if step_times:
        badges["path-step"] = min(step_times)
    finished.sort()
    if finished:
        badges["path-finisher"] = finished[0]
    if len(finished) >= 3:
        badges["path-three"] = finished[2]
    return events, badges


def launched_at(db: Session) -> datetime | None:
    """When paths went live on this database: path XP for older work is "past work" (retro)."""
    meta = db.get(AppMeta, LAUNCH_KEY)
    try:
        return _aware(datetime.fromisoformat(meta.value)) if meta else None
    except ValueError:
        return None


def mark_launch(db: Session) -> None:
    if db.get(AppMeta, LAUNCH_KEY) is None:
        db.add(AppMeta(key=LAUNCH_KEY, value=datetime.now(timezone.utc).isoformat()))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()


# ----------------------------------------------------------------------------- activity & skips

def touch(db: Session, user: User, path: str, step: str) -> None:
    now = datetime.now(timezone.utc)
    row = db.query(PathActivity).filter_by(user_id=user.id, path=path).first()
    if row is None:
        db.add(PathActivity(user_id=user.id, path=path, step=step, started_at=now, last_active_at=now))
    else:
        row.step, row.last_active_at = step, now
    try:
        db.commit()
    except IntegrityError:  # two tabs opened the path at the same moment
        db.rollback()


def skip_ahead(db: Session, user: User, path: str, step: str) -> None:
    if db.query(PathSkip.id).filter_by(user_id=user.id, path=path, step=step).first() is None:
        db.add(PathSkip(user_id=user.id, path=path, step=step))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    touch(db, user, path, step)


# ----------------------------------------------------------------------------- the step picker

def next_question(db: Session, user: User, path: Path, number: int, exclude_ids: set[int] | None = None,
                  rng: random.Random | None = None):
    """A question from the step's pool, chosen by the same adaptive picker as Practice.

    Questions the learner hasn't answered well yet come first; the level follows their mastery
    of the step's topics (kept inside the step's levels).
    """
    from app.services.learning import _question_out, _recent_question_ids

    rng = rng or random.Random()
    step = path.steps[number - 1]
    ids = pool_ids(step, _catalog(db))
    questions = db.query(Question).filter(Question.id.in_(ids)).all()
    if not questions:
        return None
    best: dict[int, float] = {}
    for qid, score in (
        db.query(Response.question_id, Feedback.overall_score)
        .join(Feedback, Feedback.response_id == Response.id)
        .filter(Response.user_id == user.id, Response.question_id.in_(ids))
        .all()
    ):
        best[qid] = max(best.get(qid, 0.0), float(score or 0.0))
    skipped = {qid for (qid,) in db.query(QuestionSkip.question_id).filter(QuestionSkip.user_id == user.id).all()}
    seen = set(best) | skipped
    recent = set(_recent_question_ids(db, user, limit=4)) | set(exclude_ids or ())

    domain_ids = {q.domain_id for q in questions}
    masteries = [m for (m,) in db.query(SkillMastery.mastery)
                 .filter(SkillMastery.user_id == user.id, SkillMastery.domain_id.in_(domain_ids)).all()]
    preferred = adaptive.mastery_to_difficulty(sum(masteries) / len(masteries) if masteries else 0.2)
    if preferred not in step.levels:
        order = list(ALL_LEVELS)
        preferred = min(step.levels, key=lambda lv: abs(order.index(lv) - order.index(preferred)))

    weak = [q for q in questions if best.get(q.id, 0.0) < PASS_MARK]
    for pool in ([q for q in weak if q.id not in recent], [q for q in questions if q.id not in recent], weak, questions):
        if pool:
            break
    cands = [{"id": q.id, "difficulty": _level(q.difficulty), "obj": q} for q in pool]
    rng.shuffle(cands)
    picked = adaptive.pick_question(candidates=cands, seen_ids=seen, preferred_difficulty=preferred)
    q = picked["obj"] if picked else pool[0]
    domain = db.get(SkillDomain, q.domain_id)
    touch(db, user, path.slug, step.key)
    return _question_out(q, domain)


# ----------------------------------------------------------------------------- read models

def _levels_label(levels: tuple[str, ...]) -> str:
    names = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"}
    if levels == ALL_LEVELS:
        return "All levels"
    return names[levels[0]] if len(levels) == 1 else f"{names[levels[0]]} to {names[levels[-1]].lower()}"


def _exercise_out(st: StepState) -> dict | None:
    if not st.exercise_slugs:
        return None
    first = EXERCISES[st.exercise_slugs[0]]
    return {
        "title": first["title"],
        "any_language": len(st.exercise_slugs) > 1,
        "options": [{"slug": s, "language": EXERCISES[s]["language"],
                     "language_name": LANGUAGE_NAMES.get(EXERCISES[s]["language"], EXERCISES[s]["language"])}
                    for s in st.exercise_slugs],
        "passed": st.exercise_passed is not None,
        "passed_slug": st.exercise_passed,
    }


def step_out(st: StepState) -> dict:
    return {
        "number": st.number,
        "key": st.step.key,
        "title": st.step.title,
        "blurb": st.step.blurb,
        "levels": _levels_label(st.step.levels),
        "status": st.status,
        "skipped": st.skipped,
        "pool_size": len(st.pool),
        "target": st.target,
        "answered": st.answered,
        "score": st.score,
        "questions_passed": st.questions_cleared_at is not None,
        "exercise": _exercise_out(st),
        "done_at": st.done_at,
    }


def path_out(ps: PathState, *, with_steps: bool = False) -> dict:
    cur = ps.current
    out = {
        "slug": ps.path.slug,
        "name": ps.path.name,
        "blurb": ps.path.blurb,
        "mark": ps.path.mark,
        "steps_total": len(ps.steps),
        "steps_done": ps.done,
        "progress": ps.fraction,
        "started": ps.started,
        "finished": ps.finished_at is not None,
        "current_step": cur.number,
        "current_title": cur.step.title,
        "exercises": sum(1 for s in ps.steps if s.exercise_slugs),
    }
    if with_steps:
        out["steps"] = [step_out(s) for s in ps.steps]
    return out


def continue_card(db: Session, user: User, states: dict[str, PathState] | None = None) -> dict | None:
    """Where to pick up: the path last opened, else the unfinished path with the most progress."""
    states = states or progress(db, user)
    pick: tuple[PathState, StepState] | None = None
    last = (
        db.query(PathActivity).filter(PathActivity.user_id == user.id)
        .order_by(PathActivity.last_active_at.desc(), PathActivity.id.desc()).all()
    )
    for act in last:
        ps = states.get(act.path)
        if ps is None or ps.finished_at is not None:
            continue
        st = next((s for s in ps.steps if s.step.key == act.step and s.status == "open"), None) or ps.current
        pick = (ps, st)
        break
    if pick is None:
        started = [ps for ps in states.values() if ps.started and ps.finished_at is None]
        if started:
            ps = max(started, key=lambda p: (p.fraction, -PATHS.index(p.path)))
            pick = (ps, ps.current)
    if pick is None:
        return None
    ps, st = pick
    return {"path": path_out(ps), "step": step_out(st), "from_history": not last}


def overview(db: Session, user: User) -> dict:
    states = progress(db, user)
    return {
        "paths": [path_out(ps) for ps in states.values()],
        "continue": continue_card(db, user, states),
        **rules(),
    }


def detail(db: Session, user: User, slug: str) -> dict:
    ps = progress(db, user, only=slug)[slug]
    return {**path_out(ps, with_steps=True), **rules()}


def rules() -> dict:
    return {"pass_mark": PASS_MARK, "step_xp": STEP_XP, "path_xp": PATH_XP}


def get_path(slug: str) -> Path | None:
    return BY_SLUG.get(slug)
