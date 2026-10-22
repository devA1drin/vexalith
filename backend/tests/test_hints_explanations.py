"""Progressive hints (generation, reveal order, penalty) and detailed explanations."""

from app.content.bank import SEED_QUESTIONS
from app.content.hints import HINT_LEVELS, build_hints
from app.db.session import SessionLocal
from app.models.models import Question
from tests.conftest import auth


def _q(pred):
    with SessionLocal() as db:
        return next(q for q in db.query(Question).all() if pred(q))


def test_every_question_has_three_distinct_hints():
    for q in SEED_QUESTIONS:
        hints = q["rubric"]["hints"]
        assert len(hints) == HINT_LEVELS and all(h.strip() for h in hints), q["title"]
        assert len(set(hints)) == HINT_LEVELS, q["title"]


def test_fill_blank_hints_never_reveal_the_whole_answer():
    for q in SEED_QUESTIONS:
        r = q["rubric"]
        if r.get("kind") == "fill_blank" and len(r["accepted_answers"][0]) > 3:
            assert r["accepted_answers"][0] not in r["hints"][2], q["title"]


def test_explicit_hints_are_kept():
    q = {"domain": "debugging", "rubric": {"hints": ["a", "b", "c", "d"], "concepts": []}}
    assert build_hints(q) == ["a", "b", "c"]


def test_hints_reveal_one_level_at_a_time_and_cap(client):
    h = auth(pid="hint-reveal")
    q = _q(lambda x: True)
    assert client.get(f"/api/questions/{q.id}/hints", headers=h).json()["revealed"] == []
    seen = []
    for level in range(1, 5):
        r = client.post(f"/api/questions/{q.id}/hints", headers=h).json()
        seen.append(len(r["revealed"]))
        assert r["hint_count"] == 3
    assert seen == [1, 2, 3, 3]  # capped at three
    assert r["revealed"] == q.rubric["hints"] and r["penalty"] == 0.3
    nxt = client.get("/api/questions/next?language=python", headers=h).json()
    assert nxt["hint_count"] == 3


def test_hint_penalty_applies_to_the_answer_and_resets_after(client):
    h = auth(pid="hint-penalty")
    q = _q(lambda x: (x.rubric or {}).get("kind") == "fill_blank")
    ans = q.rubric["accepted_answers"][0] + " because " + q.rubric["reference_answer"]
    base = client.post("/api/responses", headers=auth(pid="hint-none"), json={"question_id": q.id, "answer_text": ans}).json()["feedback"]
    client.post(f"/api/questions/{q.id}/hints", headers=h)
    client.post(f"/api/questions/{q.id}/hints", headers=h)
    fb = client.post("/api/responses", headers=h, json={"question_id": q.id, "answer_text": ans}).json()["feedback"]
    assert fb["hints_used"] == 2 and fb["hint_penalty"] == 0.2
    assert abs(fb["overall_score"] - round(base["overall_score"] * 0.8, 3)) < 0.002
    # A new attempt starts with no hints revealed.
    assert client.get(f"/api/questions/{q.id}/hints", headers=h).json()["revealed"] == []
    again = client.post("/api/responses", headers=h, json={"question_id": q.id, "answer_text": ans}).json()["feedback"]
    assert again["hints_used"] == 0


def test_explanations_for_correct_and_incorrect_answers(client):
    h = auth(pid="explain")
    fill = _q(lambda x: (x.rubric or {}).get("kind") == "fill_blank")
    wrong = client.post("/api/responses", headers=h, json={"question_id": fill.id, "answer_text": "no idea"}).json()["feedback"]
    assert wrong["verdict"] == "incorrect"
    assert wrong["accepted_answers"] == fill.rubric["accepted_answers"]
    assert wrong["key_points"] == [c["label"] for c in fill.rubric["concepts"]]
    assert wrong["reference_answer"] == fill.rubric["reference_answer"]

    normal = _q(lambda x: not (x.rubric or {}).get("kind") and x.rubric.get("misconceptions"))
    right = client.post("/api/responses", headers=h, json={"question_id": normal.id, "answer_text": normal.rubric["reference_answer"]}).json()["feedback"]
    assert right["verdict"] == "correct" and right["accepted_answers"] == []
    assert right["key_points"][0] == normal.rubric["concepts"][0]["label"]
    # A misconception answer gets the matching explanation.
    m = normal.rubric["misconceptions"][0]
    bad = client.post("/api/responses", headers=h, json={"question_id": normal.id, "answer_text": f"I think {m['keywords'][0]} happens here."}).json()["feedback"]
    assert any(x["explanation"] == m["explanation"] for x in bad["misconceptions"])
