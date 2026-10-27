"""Admin changes to questions: text edits, hiding, new questions, house-style checks.

Seeding rewrites built-in questions from code on every start, so edits are stored in
``question_edits`` and applied again right after each seed (and at once on save).
"""

from __future__ import annotations

import copy
import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.hints import build_hints
from app.content.humanize import humanize
from app.content.qdef import Q
from app.models.models import Difficulty, Question, QuestionEdit, SkillDomain

KEY = "Key idea:"
MAX_TEXT = 2000


def hidden_ids(db: Session) -> set[int]:
    return set(db.scalars(select(QuestionEdit.question_id).where(QuestionEdit.hidden == 1)))


def split_prompt(prompt: str) -> tuple[str, str]:
    """(question text, task line). Prompts are "question\\n\\ntask line"."""
    head, sep, tail = (prompt or "").rpartition("\n\n")
    return (head, tail) if sep else (prompt or "", "")


def key_idea_of(rubric: dict) -> str:
    for h in rubric.get("hints") or []:
        if h.startswith(KEY):
            return h[len(KEY):].strip()
    return ""


def _apply(q: Question, e: QuestionEdit) -> None:
    rubric = copy.deepcopy(q.rubric or {})
    if e.question_text is not None:
        _, task = split_prompt(q.prompt)
        q.prompt = e.question_text.strip() + (f"\n\n{task}" if task else "")
    if e.reference_answer is not None:
        rubric["reference_answer"] = e.reference_answer.strip()
    if e.key_idea is not None:
        hints = list(rubric.get("hints") or [])
        line = f"{KEY} {e.key_idea.strip()}"
        idx = next((i for i, h in enumerate(hints) if h.startswith(KEY)), None)
        if idx is None:
            hints.insert(min(1, len(hints)), line)
        else:
            hints[idx] = line
        rubric["hints"] = hints
    q.rubric = rubric


def apply_all(db: Session) -> int:
    edits = db.scalars(select(QuestionEdit)).all()
    n = 0
    for e in edits:
        q = db.get(Question, e.question_id)
        if q is not None and (e.question_text is not None or e.reference_answer is not None or e.key_idea is not None):
            _apply(q, e)
            n += 1
    if n:
        db.commit()
    return n


def _edit_row(db: Session, qid: int) -> QuestionEdit:
    e = db.get(QuestionEdit, qid)
    if e is None:
        e = QuestionEdit(question_id=qid, hidden=0)
        db.add(e)
    return e


def edit(db: Session, q: Question, *, question_text: str | None, reference_answer: str | None, key_idea: str | None) -> dict:
    """Save the changed fields (None = leave alone). Returns {field: [before, after]}."""
    rubric = q.rubric or {}
    before = {
        "question_text": split_prompt(q.prompt)[0],
        "reference_answer": rubric.get("reference_answer", ""),
        "key_idea": key_idea_of(rubric),
    }
    wanted = {"question_text": question_text, "reference_answer": reference_answer, "key_idea": key_idea}
    changes = {k: [before[k], v.strip()] for k, v in wanted.items() if v is not None and v.strip() != before[k]}
    if not changes:
        return {}
    e = _edit_row(db, q.id)
    for k, (_old, new) in changes.items():
        setattr(e, k, new)
    e.updated_at = datetime.now(timezone.utc)
    _apply(q, e)
    return changes


def set_hidden(db: Session, q: Question, hidden: bool) -> bool:
    e = _edit_row(db, q.id)
    changed = bool(e.hidden) != hidden
    e.hidden = 1 if hidden else 0
    e.updated_at = datetime.now(timezone.utc)
    return changed


# ----------------------------------------------------------------------------- house style

_DIRECTIONS = re.compile(
    r"\b(in your own words|explain your (answer|reasoning)|write your answer|answer (below|in the box|here)"
    r"|be (specific|detailed|clear)|show your (work|reasoning)|justify your answer|please)\b",
    re.I,
)
_LINE_BY_LINE = re.compile(r"\b(line by line|line-by-line|lines? \d+|step \d+)\b", re.I)
_NUMBERED = re.compile(r"^\s*(\d+[.)]|[-*])\s", re.M)


def style_notes(question_text: str | None, key_idea: str | None, reference_answer: str | None = None) -> list[str]:
    """Gentle house-style checks. Warnings only; the editor shows them before saving."""
    notes: list[str] = []
    if question_text is not None:
        m = _DIRECTIONS.search(question_text)
        if m:
            notes.append(f"The task line under the question already says how to answer, so “{m.group(0)}” can go.")
        if len(question_text) > 500:
            notes.append("The question is long. One or two sentences usually do it.")
        if question_text.strip() and question_text.strip()[-1] not in ".?!:)`":
            notes.append("End the question with a full stop or a question mark.")
    for label, text in (("explanation", key_idea), ("model answer", reference_answer)):
        if text is None:
            continue
        if _LINE_BY_LINE.search(text) or len(_NUMBERED.findall(text)) >= 3:
            notes.append(f"The {label} reads like a line-by-line walkthrough. Say the main idea and why it works instead.")
    if key_idea is not None:
        if len(key_idea.strip()) < 40:
            notes.append("The explanation is very short. Give the main idea and a strategy that carries over to similar problems.")
        if len(key_idea) > 600:
            notes.append("The explanation is long. Keep it to the idea, the strategy, and the usual mistake.")
    return notes


# ----------------------------------------------------------------------------- new questions

def _keywords(label: str) -> list[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-z_][A-Za-z0-9_+#]*", label) if len(w) > 3]
    return words[:6] or [label.lower()[:40]]


def parse_points(text: str) -> list[tuple[str, list[str]]]:
    """Key points, one per line: "Label — keyword, keyword" (keywords optional)."""
    out = []
    for raw in (text or "").splitlines():
        line = raw.strip().lstrip("-*• ").strip()
        if not line:
            continue
        parts = re.split(r"\s+[—–-]\s+", line, maxsplit=1)
        label = parts[0].strip()
        keywords = [k.strip().lower() for k in parts[1].split(",") if k.strip()] if len(parts) > 1 else _keywords(label)
        out.append((label[:120], keywords[:8]))
    return out[:6]


def create(db: Session, *, domain: SkillDomain, difficulty: str, language: str, title: str, code: str,
           question_text: str, key_points: str, reference_answer: str, key_idea: str) -> Question:
    points = parse_points(key_points)
    if not points:
        raise ValueError("Add at least one key point a good answer should mention.")
    n = len(points)
    weights = [round(1.0 / n, 3)] * n
    item = Q(domain.slug, difficulty, language, title.strip(), code.rstrip(), question_text.strip(),
             [(lbl, kws, w) for (lbl, kws), w in zip(points, weights)], [], reference_answer.strip())
    item["rubric"]["hints"] = build_hints(item)
    humanize(item)
    rubric = item["rubric"]
    if key_idea.strip():
        hints = list(rubric["hints"])
        idx = next((i for i, h in enumerate(hints) if h.startswith(KEY)), None)
        line = f"{KEY} {key_idea.strip()}"
        if idx is None:
            hints.insert(min(1, len(hints)), line)
        else:
            hints[idx] = line
        rubric["hints"] = hints
    q = Question(domain_id=domain.id, title=item["title"], code=item["code"], prompt=item["prompt"],
                 difficulty=Difficulty(difficulty), language=language, rubric=rubric, source="admin")
    db.add(q)
    db.flush()
    return q
