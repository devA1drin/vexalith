"""Difficulty choice, topic filter, open-by-id and personalised recommendations."""

import pytest

from app.db.session import SessionLocal
from app.models.models import Question
from tests.conftest import auth


@pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
@pytest.mark.parametrize("lang", ["python", "cpp", "css"])
def test_fixed_level_only_serves_that_level_in_that_language(client, lang, level):
    h = auth(pid=f"lvl-{lang}-{level}")
    exclude: list[int] = []
    for _ in range(8):
        q = client.get(
            f"/api/questions/next?language={lang}&difficulty={level}&exclude={','.join(map(str, exclude[-12:]))}",
            headers=h,
        ).json()
        assert q["difficulty"] == level
        assert q["language"] in (lang, "general")
        exclude.append(q["id"])
        # Skip keeps the level and the language too.
        s = client.post(f"/api/questions/{q['id']}/skip?language={lang}&difficulty={level}", headers=h).json()
        assert s["next_question"]["difficulty"] == level
        assert s["next_question"]["language"] in (lang, "general")
        assert s["next_question"]["id"] != q["id"]


def test_adaptive_is_the_default_and_accepted_explicitly(client):
    h = auth(pid="lvl-adaptive")
    assert client.get("/api/questions/next?language=python&difficulty=adaptive", headers=h).status_code == 200
    assert client.get("/api/questions/next?language=python&difficulty=expert", headers=h).status_code == 422


def test_new_learner_with_fixed_level_still_starts_in_fundamentals(client):
    q = client.get("/api/questions/next?language=javascript&difficulty=intermediate", headers=auth(pid="lvl-new")).json()
    assert q["domain_slug"] == "fundamentals" and q["difficulty"] == "intermediate"


def test_topic_filter_and_open_by_id(client):
    h = auth(pid="topic")
    for _ in range(5):
        q = client.get("/api/questions/next?language=python&topic=debugging", headers=h).json()
        assert q["domain_slug"] == "debugging" and q["language"] in ("python", "general")
    one = client.get(f"/api/questions/{q['id']}", headers=h).json()
    assert one["id"] == q["id"] and one["title"] == q["title"]
    assert client.get("/api/questions/999999", headers=h).status_code == 404
    assert client.get("/api/questions/next?topic=DROP%20TABLE", headers=h).status_code == 422


def test_recommendations_for_a_new_learner(client):
    r = client.get("/api/recommendations?language=cpp", headers=auth(pid="rec-new")).json()
    assert r["language"] == "cpp" and r["languages"] == []
    assert 1 <= len(r["topics"]) <= 3 and r["next_questions"]
    assert all(q["language"] in ("cpp", "general") for q in r["next_questions"])
    assert r["headline"].startswith("Start with the basics")


def test_recommendations_point_at_the_weakest_skill_and_language(client):
    h = auth(pid="rec-weak")
    with SessionLocal() as db:
        qs = db.query(Question).all()
        py_ok = [q for q in qs if q.language == "python" and not (q.rubric or {}).get("kind")][:3]
        js_bad = [q for q in qs if q.language == "javascript" and not (q.rubric or {}).get("kind")][:3]
        py_ok = [(q.id, q.rubric["reference_answer"]) for q in py_ok]
        js_bad = [(q.id, q.domain_id) for q in js_bad]
    for qid, ref in py_ok:
        client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": ref})
    for qid, _ in js_bad:
        client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "I am not sure at all."})
    r = client.get("/api/recommendations?language=javascript", headers=h).json()
    assert [l["language"] for l in r["languages"]] == ["javascript"]
    prog = client.get("/api/progress", headers=h).json()
    eligible = {t["domain_slug"] for t in r["topics"]}
    weakest = min(
        (d for d in prog["domains"] if d["domain_slug"] in eligible),
        key=lambda d: d["mastery"],
    )
    assert r["topics"][0]["mastery"] == pytest.approx(weakest["mastery"], abs=0.006)
    answered = {qid for qid, _ in py_ok + js_bad}
    assert not answered & {q["id"] for q in r["next_questions"]}


def test_recommendations_require_sign_in(client):
    assert client.get("/api/recommendations").status_code == 401
