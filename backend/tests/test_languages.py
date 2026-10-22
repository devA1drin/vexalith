"""Language-aware selection and non-destructive reseeding."""

from collections import Counter

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.content.bank import SEED_QUESTIONS
from tests.conftest import auth

MARKUP_DOMAINS = {"fundamentals", "code_tracing", "debugging", "edge_cases_testing", "code_review_design", "logic_problems", "algorithms"}


def _walk(client, h, lang, n=25):
    q = client.get(f"/api/questions/next?language={lang}", headers=h).json()
    out = [q]
    for _ in range(n):
        q = client.post(f"/api/questions/{q['id']}/skip?language={lang}", headers=h).json()["next_question"]
        out.append(q)
    return out


def test_each_language_returns_appropriate_questions(client):
    for i, lang in enumerate(["python", "javascript", "php", "html", "css"]):
        qs = _walk(client, auth(pid=f"lang-{i}"), lang)
        assert {q["language"] for q in qs} <= {lang, "general"}
        assert any(q["language"] == lang for q in qs)
        if lang in ("html", "css"):
            assert {q["domain_slug"] for q in qs} <= MARKUP_DOMAINS
        # consecutive questions never repeat
        assert all(a["id"] != b["id"] for a, b in zip(qs, qs[1:]))


def graduate(client, h, lang, n=5):
    """Answer n fundamentals questions with their model answers so onboarding ends."""
    for _ in range(n):
        q = client.get(f"/api/questions/next?language={lang}", headers=h).json()
        assert q["domain_slug"] == "fundamentals"
        ref = next(x for x in SEED_QUESTIONS if x["title"] == q["title"] and x["language"] == q["language"])
        r = client.post("/api/responses", headers=h, json={"question_id": q["id"], "answer_text": ref["rubric"]["reference_answer"]})
        assert r.status_code == 201


def test_general_selection_is_language_agnostic(client):
    h = auth(pid="lang-general")
    graduate(client, h, "general")
    qs = _walk(client, h, "general", n=30)
    assert {q["language"] for q in qs} == {"general"}
    assert {q["domain_slug"] for q in qs} <= {"fundamentals", "logic_problems", "algorithms"}
    assert {"logic_problems", "algorithms"} <= {q["domain_slug"] for q in qs}


def test_logic_and_algorithms_surface_under_a_language(client):
    h = auth(pid="lang-mix")
    graduate(client, h, "python")
    domains = Counter(q["domain_slug"] for q in _walk(client, h, "python", n=60))
    assert domains["logic_problems"] > 0 and domains["algorithms"] > 0


def test_unknown_language_rejected(client):
    r = client.get("/api/questions/next?language=cobol", headers=auth(pid="lang-x"))
    assert r.status_code == 422


def test_reseed_adds_content_without_touching_user_data(tmp_path, monkeypatch):
    from app.content import bank, domains as dom
    from app.models.models import Question, Response, SkillDomain, User
    from app.services import question_bank as qb

    engine = create_engine(f"sqlite:///{tmp_path}/v2.db")
    qb.migrate_schema(engine)
    old_q = [q for q in bank.SEED_QUESTIONS if q["language"] in ("python", "javascript") and q["domain"] not in ("algorithms", "logic_problems")]
    old_d = [d for d in dom.DOMAINS if d["slug"] not in ("algorithms", "logic_problems")]
    monkeypatch.setattr(qb, "SEED_QUESTIONS", old_q)
    monkeypatch.setattr(qb, "DOMAINS", old_d)
    with Session(engine) as db:
        qb.seed_domains_and_questions(db)
        before = {(q.title, q.language): q.id for q in db.query(Question).all()}
        u = User(auth_provider="github", provider_account_id="keep", display_name="Keep")
        db.add(u)
        db.flush()
        db.add(Response(user_id=u.id, question_id=next(iter(before.values())), answer_text="kept"))
        db.commit()

    monkeypatch.setattr(qb, "SEED_QUESTIONS", bank.SEED_QUESTIONS)
    monkeypatch.setattr(qb, "DOMAINS", dom.DOMAINS)
    assert qb.migrate_schema(engine) is False  # no reset
    with Session(engine) as db:
        qb.seed_domains_and_questions(db)
        after = {(q.title, q.language): q.id for q in db.query(Question).all()}
        assert all(after[k] == v for k, v in before.items())  # existing ids unchanged
        assert len(after) == len(bank.SEED_QUESTIONS)
        assert db.query(Response).count() == 1 and db.query(User).count() == 1
        assert {"algorithms", "logic_problems"} <= {d.slug for d in db.query(SkillDomain).all()}
