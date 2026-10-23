"""Looping drills and fill-in-the-missing-code questions: coverage, API kind and short answers."""

from collections import Counter

from app.ai.heuristic import fill_blank_hit
from app.content.bank import SEED_QUESTIONS
from app.content.qdef import BLANK
from app.content.questions_loops import QUESTIONS_LOOPS
from app.content.questions_missing_code import QUESTIONS_MISSING_CODE
from app.models.models import Question
from tests.conftest import auth

LEVELS = {"beginner", "intermediate", "advanced"}
CODE_LANGS = ("python", "javascript", "php", "cpp")


def test_loop_drills_per_language_and_level():
    counts = Counter((q["language"], q["difficulty"]) for q in QUESTIONS_LOOPS)
    for lang in CODE_LANGS:
        for level in LEVELS:
            assert counts[(lang, level)] >= 2, (lang, level)
    assert sum(1 for q in QUESTIONS_LOOPS if q["language"] == "general") >= 3


def test_missing_code_for_every_language():
    counts = Counter(q["language"] for q in QUESTIONS_MISSING_CODE)
    for lang in CODE_LANGS:
        assert counts[lang] >= 6, lang
        assert {q["difficulty"] for q in QUESTIONS_MISSING_CODE if q["language"] == lang} == LEVELS
    for lang in ("html", "css", "general"):
        assert counts[lang] >= 3, lang


def test_every_missing_code_question_is_well_formed():
    for q in QUESTIONS_MISSING_CODE:
        r = q["rubric"]
        assert r["kind"] == "fill_blank" and q["code"].count(BLANK) == 1, q["title"]
        assert all(fill_blank_hit(a, r["accepted_answers"]) for a in r["accepted_answers"]), q["title"]
        assert fill_blank_hit(r["reference_answer"], r["accepted_answers"]), q["title"]
    assert all(q in SEED_QUESTIONS for q in QUESTIONS_MISSING_CODE + QUESTIONS_LOOPS)


def _fill_blank_question(lang):
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        return next(q for q in db.query(Question).filter_by(language=lang).all() if (q.rubric or {}).get("kind") == "fill_blank")


def test_api_marks_fill_blank_questions_and_accepts_short_answers(client):
    h = auth(pid="blank-api")
    q = _fill_blank_question("cpp")
    accepted = q.rubric["accepted_answers"][0]
    r = client.post("/api/responses", headers=h, json={"question_id": q.id, "answer_text": accepted})
    assert r.status_code == 201
    assert r.json()["feedback"]["verdict"] == "correct"
    # Explain questions still need a real explanation.
    other = next(x for x in SEED_QUESTIONS if "kind" not in x["rubric"])
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        oid = db.query(Question).filter_by(title=other["title"], language=other["language"]).one().id
    assert client.post("/api/responses", headers=h, json={"question_id": oid, "answer_text": "i++"}).status_code == 422


def test_question_out_exposes_kind(client):
    h = auth(pid="blank-kind")
    kinds = set()
    q = client.get("/api/questions/next?language=css&focus=fundamentals", headers=h).json()
    for _ in range(40):
        kinds.add(q["kind"])
        q = client.post(f"/api/questions/{q['id']}/skip?language=css&focus=fundamentals", headers=h).json()["next_question"]
    assert kinds == {"explain", "fill_blank"}


def test_public_catalog_counts_match_the_seed_bank(client):
    data = client.get("/api/catalog").json()
    assert data["total"] == len(SEED_QUESTIONS)
    assert data["languages"]["cpp"] == sum(1 for q in SEED_QUESTIONS if q["language"] == "cpp")
    assert data["kinds"]["fill_blank"] == sum(1 for q in SEED_QUESTIONS if q["rubric"].get("kind") == "fill_blank")
