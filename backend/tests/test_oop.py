"""Object-Oriented Programming (oop) domain, question bank, topic filter, fill-blank and Filipino support."""

from collections import Counter

import pytest

from app.ai.filipino import gloss, lemma
from app.ai.heuristic import grade
from app.ai.provider import QuestionContext
from app.content.bank import SEED_QUESTIONS
from app.content.domains import DOMAINS
from app.db.session import SessionLocal
from app.models.models import Question
from tests.conftest import auth

LEVELS = ("beginner", "intermediate", "advanced")
OOP_LANGS = ("python", "javascript", "php", "cpp", "general")


def test_oop_domain_is_registered(client):
    slugs = [d["slug"] for d in DOMAINS]
    assert "oop" in slugs
    api_domains = client.get("/api/domains").json()
    assert any(d["slug"] == "oop" and d["name"] == "Object-Oriented Programming" for d in api_domains)


def test_oop_coverage_by_language_level_and_kind():
    oop = [q for q in SEED_QUESTIONS if q["domain"] == "oop"]
    assert len(oop) >= 45
    by_lang_level = Counter((q["language"], q["difficulty"]) for q in oop)
    for lang in OOP_LANGS:
        for level in LEVELS:
            assert by_lang_level[(lang, level)] >= 2, (lang, level)
    for lang in ("python", "javascript", "php", "cpp"):
        blanks = [q for q in oop if q["language"] == lang and q["rubric"].get("kind") == "fill_blank"]
        assert len(blanks) >= 3, lang


def test_every_oop_question_has_three_distinct_hints_and_passes_rubric():
    oop = [q for q in SEED_QUESTIONS if q["domain"] == "oop"]
    for q in oop:
        hints = q["rubric"].get("hints") or []
        assert len(hints) == 3 and len(set(hints)) == 3, q["title"]
        ctx = QuestionContext(q["title"], q["language"], q["code"], q["prompt"], q["domain"], q["difficulty"], q["rubric"])
        fb = grade(q["rubric"]["reference_answer"], ctx)
        assert fb.verdict == "correct" and fb.correctness_score >= 0.75 and not fb.misconceptions, q["title"]


@pytest.mark.parametrize("lang", ["python", "javascript", "php", "cpp", "general", "html", "css"])
def test_topic_oop_filter_across_all_languages_without_leakage(client, lang):
    h = auth(pid=f"oop-topic-{lang}")
    q = client.get(f"/api/questions/next?language={lang}&topic=oop", headers=h).json()
    assert q["domain_slug"] == "oop"
    assert q["language"] in (lang, "general")
    for _ in range(5):
        s = client.post(f"/api/questions/{q['id']}/skip?language={lang}&topic=oop", headers=h).json()
        nxt = s["next_question"]
        assert nxt["domain_slug"] == "oop"
        assert nxt["language"] in (lang, "general")
        assert nxt["id"] != q["id"]
        q = nxt


def test_fill_blank_oop_grading_via_api(client):
    h = auth(pid="oop-blank")
    with SessionLocal() as db:
        q = db.query(Question).filter_by(title="Missing code: store the constructor argument on self", language="python").one()
        qid = q.id
    r = client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "self.name = name"})
    assert r.status_code == 201
    fb = r.json()["feedback"]
    assert fb["verdict"] == "correct" and fb["correctness_score"] >= 0.8


@pytest.mark.parametrize("word,expected_term", [
    ("klase", "class"),
    ("bagay", "object"),
    ("katangian", "property"),
    ("paraan", "method"),
    ("mana", "inherit"),
    ("minana", "inherited"),
    ("nagmamana", "inherits"),
    ("magulang", "parent"),
    ("anak", "child"),
    ("tagagawa", "constructor"),
    ("pribado", "private"),
    ("nakatago", "private"),
    ("pampubliko", "public"),
    ("halimbawa", "instance"),
])
def test_filipino_oop_terms_map_to_rubric_keywords(word, expected_term):
    got = lemma(word)
    assert got is not None
    opts = [o.strip() for o in got[1].split("|")]
    assert expected_term in opts, (word, opts)


def test_filipino_and_taglish_oop_answers_grade_correctly():
    q = next(x for x in SEED_QUESTIONS if x["title"] == "A Counter class and two instances")
    ctx = QuestionContext(q["title"], q["language"], q["code"], q["prompt"], q["domain"], q["difficulty"], q["rubric"])
    fil = (
        "Ang lalabas ay 2 1. Ang a at b ay magkahiwalay na halimbawa ng klase na Counter, "
        "kaya may sariling katangian na self.count ang bawat bagay na sinisimulan ng __init__ sa 0."
    )
    taglish = (
        "Mag-print siya ng 2 1 kasi magkaibang bagay o instance ang a at b ng klase na Counter, "
        "at ang tagagawa na __init__ ay nagse-set ng sariling self.count = 0 sa bawat object."
    )
    for ans in (fil, taglish):
        fb = grade(ans, ctx)
        assert fb.answer_language in ("fil", "taglish")
        assert fb.verdict == "correct" and fb.correctness_score == 1.0, (ans, fb.missed_concepts, gloss(ans))
