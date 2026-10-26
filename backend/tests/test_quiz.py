"""Timed quizzes: setup, picking, the server-side clock, answers, results, history, XP and the badge."""

import random
from datetime import timedelta, timezone

import pytest

from app.content.paths import BY_SLUG as PATHS
from app.db.session import SessionLocal
from app.models.models import (
    Question,
    QuizAnswer,
    QuizSession,
    Response,
    User,
    UserBadge,
    XpEvent,
)
from app.services import paths, quiz
from tests.conftest import auth


@pytest.fixture(autouse=True, scope="module")
def _off_the_leaderboard():
    """These learners earn XP this week; hide them afterwards so they don't crowd the board tests."""
    yield
    from app.models.models import LearnerProfile

    with SessionLocal() as db:
        for prof in (db.query(LearnerProfile).join(User, User.id == LearnerProfile.user_id)
                     .filter(User.provider_account_id.like("qz-%"))):
            prof.visibility = "hidden"
        db.commit()

UTC = timezone.utc
WRONG = "I am not sure what it does at all"
TAGLISH = "Mag-print siya ng value kasi yung loop ay nag-stop bago ma-add ang last number, kaya kulang ang total."


def _user(client, pid):
    client.get("/api/me", headers=auth(pid=pid))
    with SessionLocal() as db:
        return db.query(User).filter_by(provider_account_id=pid).one().id


def _good(qid):
    with SessionLocal() as db:
        r = db.get(Question, qid).rubric
        return (r.get("accepted_answers") or [None])[0] if r.get("kind") == "fill_blank" else r["reference_answer"]


def _start(client, pid, **body):
    payload = {"scope": "language", "value": "python", "length": 5, "minutes": 5, "instant": False, **body}
    return client.post("/api/quiz", json=payload, headers=auth(pid=pid))


def _qids(quiz_id):
    with SessionLocal() as db:
        return list(db.get(QuizSession, quiz_id).question_ids)


def _answer(client, pid, quiz_id, position, text):
    return client.post(f"/api/quiz/{quiz_id}/answer", json={"position": position, "answer_text": text}, headers=auth(pid=pid))


def _shift(quiz_id, seconds):
    """Move a quiz's clock into the past, as if `seconds` had gone by."""
    with SessionLocal() as db:
        q = db.get(QuizSession, quiz_id)
        q.started_at = q.started_at - timedelta(seconds=seconds)
        q.deadline_at = q.deadline_at - timedelta(seconds=seconds)
        db.commit()


def _finish(client, pid, quiz_id):
    r = client.post(f"/api/quiz/{quiz_id}/finish", headers=auth(pid=pid))
    assert r.status_code == 200, r.text
    return r.json()


def test_quiz_needs_sign_in(client):
    assert client.get("/api/quiz/options").status_code == 401
    assert client.post("/api/quiz", json={}).status_code == 401
    assert client.get("/api/quiz/history").status_code == 401


def test_options_offer_topics_languages_paths_lengths_and_limits(client):
    _user(client, "qz-options")
    d = client.get("/api/quiz/options", headers=auth(pid="qz-options")).json()
    assert d["lengths"] == [5, 10, 20] and d["minutes"] == [5, 10, 15]
    assert {"python", "javascript", "cpp", "java", "php"} <= {o["value"] for o in d["scopes"]["language"]}
    assert {"debugging", "code_tracing"} <= {o["value"] for o in d["scopes"]["topic"]}
    assert "python" in {o["value"] for o in d["scopes"]["path"]}
    assert all(o["count"] >= 5 for v in d["scopes"].values() for o in v)
    assert d["active"] is None and d["rules"]["quiz_xp"] == 3


def test_start_checks_its_choices(client):
    pid = "qz-validate"
    _user(client, pid)
    assert _start(client, pid, length=7).status_code == 422
    assert _start(client, pid, minutes=60).status_code == 422
    assert _start(client, pid, scope="planet").status_code == 422
    assert _start(client, pid, scope="topic", value="no_such_topic").status_code == 404
    assert _start(client, pid, scope="path", value="cobol").status_code == 404


def test_picks_short_questions_in_scope_easy_to_hard(client):
    uid = _user(client, "qz-pick")
    with SessionLocal() as db:
        user = db.get(User, uid)
        pool = quiz._pool(db, "language", "python")
        ids = quiz.pick(db, user, pool, 20, random.Random(7))
        qs = {q.id: q for q in db.query(Question).filter(Question.id.in_(ids))}
        assert len(ids) == len(set(ids)) == 20 and all(qs[i].language == "python" for i in ids)
        order = [quiz.LEVELS.index(quiz._level(qs[i].difficulty)) for i in ids]
        assert order == sorted(order)
        short = sum(1 for i in ids if quiz._kind(qs[i]) == "fill_blank" or quiz._is_short(qs[i]))
        assert short >= 18
        # A path quiz only uses that path's questions.
        catalog = paths._catalog(db)
        path_ids = {qid for s in PATHS["web"].steps for qid in paths.pool_ids(s, catalog)}
        assert set(quiz.pick(db, user, quiz._pool(db, "path", "web"), 10)) <= path_ids


def test_the_clock_lives_on_the_server_and_survives_a_refresh(client):
    pid = "qz-clock"
    _user(client, pid)
    r = _start(client, pid, minutes=10)
    assert r.status_code == 201
    s = r.json()
    assert s["status"] == "active" and s["time_limit_s"] == 600 and 595 <= s["remaining_s"] <= 600
    assert s["current"] == 0 and s["question"]["id"] == _qids(s["id"])[0] and len(s["slots"]) == 5
    _shift(s["id"], 120)  # two minutes later, the learner refreshes the page
    again = client.get(f"/api/quiz/{s['id']}", headers=auth(pid=pid)).json()
    assert 475 <= again["remaining_s"] <= 480  # not reset to 10:00
    # Only one quiz at a time; starting another points at the running one.
    clash = _start(client, pid)
    assert clash.status_code == 409 and clash.json()["quiz_id"] == s["id"]
    opts = client.get("/api/quiz/options", headers=auth(pid=pid)).json()
    assert opts["active"]["id"] == s["id"]
    # Somebody else's quiz is invisible.
    _user(client, "qz-clock-other")
    assert client.get(f"/api/quiz/{s['id']}", headers=auth(pid="qz-clock-other")).status_code == 404


def test_feedback_waits_for_the_end_and_xp_waits_too(client):
    pid = "qz-end"
    uid = _user(client, pid)
    s = _start(client, pid).json()
    qids = _qids(s["id"])
    out = _answer(client, pid, s["id"], 0, _good(qids[0]))
    assert out.status_code == 200
    out = out.json()
    assert out["feedback"] is None and out["slots"][0]["verdict"] is None and out["current"] == 1
    # The header's XP sync mid-quiz can't give the result away.
    assert client.post("/api/xp/sync", headers=auth(pid=pid)).status_code == 200
    with SessionLocal() as db:
        assert db.query(XpEvent).filter_by(user_id=uid, key=f"answer:{qids[0]}").count() == 0
    assert client.get(f"/api/quiz/{s['id']}/results", headers=auth(pid=pid)).status_code == 409
    assert _answer(client, pid, s["id"], 0, "again").status_code == 409  # one answer per question
    assert _answer(client, pid, s["id"], 1, "   ").status_code == 422
    res = _finish(client, pid, s["id"])
    assert res["status"] == "finished" and res["ended_by"] == "ended" and res["correct"] == 1
    with SessionLocal() as db:
        assert db.query(XpEvent).filter_by(user_id=uid, key=f"answer:{qids[0]}").count() == 1
    assert res["xp"] > 0


def test_instant_mode_shows_feedback_after_each_answer_in_english_or_taglish(client):
    pid = "qz-instant"
    _user(client, pid)
    s = _start(client, pid, instant=True).json()
    qids = _qids(s["id"])
    out = _answer(client, pid, s["id"], 0, _good(qids[0])).json()
    assert out["feedback"]["verdict"] == "correct" and out["slots"][0]["verdict"] == "correct"
    out = _answer(client, pid, s["id"], 1, TAGLISH).json()
    assert out["feedback"]["answer_language"] in ("fil", "taglish")


def test_time_out_finishes_the_quiz_grades_what_was_typed_and_refuses_late_answers(client):
    pid = "qz-timeout"
    uid = _user(client, pid)
    s = _start(client, pid, minutes=5).json()
    qids = _qids(s["id"])
    _answer(client, pid, s["id"], 0, _good(qids[0]))
    with SessionLocal() as db:  # an answer saved but not graded yet (e.g. the grader was slow)
        slot = db.query(QuizAnswer).filter_by(quiz_id=s["id"], position=1).one()
        slot.answer_text = _good(qids[1])
        db.commit()
    _shift(s["id"], 300 + quiz.GRACE_S + 1)
    late = _answer(client, pid, s["id"], 2, "too late")
    assert late.status_code == 409
    res = client.get(f"/api/quiz/{s['id']}/results", headers=auth(pid=pid)).json()
    assert res["ended_by"] == "time" and res["correct"] == 2 and res["time_used_s"] == 300
    assert [q["status"] for q in res["questions"]] == ["correct", "correct", "unanswered", "unanswered", "unanswered"]
    # The ones it ran out on are now in mistake review.
    rv = client.get("/api/review", headers=auth(pid=pid)).json()
    timed_out = {i["id"] for i in rv["items"] if i["reason"] == "timeout"}
    assert timed_out == set(qids[2:])
    with SessionLocal() as db:
        assert db.query(Response).filter_by(user_id=uid).count() == 2


def test_an_answer_just_after_zero_is_still_accepted(client):
    pid = "qz-grace"
    _user(client, pid)
    s = _start(client, pid, minutes=5).json()
    qids = _qids(s["id"])
    _shift(s["id"], 302)  # the auto-submit lands two seconds late
    assert _answer(client, pid, s["id"], 0, _good(qids[0])).status_code == 200


def test_skipped_questions_come_back_and_answering_everything_ends_it(client):
    pid = "qz-skip"
    _user(client, pid)
    s = _start(client, pid).json()
    qids = _qids(s["id"])
    st = client.post(f"/api/quiz/{s['id']}/skip", json={"position": 0}, headers=auth(pid=pid)).json()
    assert st["current"] == 1 and st["slots"][0]["state"] == "skipped"
    for pos in range(1, 5):
        st = _answer(client, pid, s["id"], pos, WRONG if pos == 4 else _good(qids[pos])).json()
    assert st["current"] == 0 and st["returning"] is True
    st = _answer(client, pid, s["id"], 0, _good(qids[0])).json()
    assert st["status"] == "finished"
    res = client.get(f"/api/quiz/{s['id']}/results", headers=auth(pid=pid)).json()
    assert res["ended_by"] == "done" and res["correct"] == 4 and res["to_review"] == 1
    miss = res["questions"][4]
    assert miss["status"] == "wrong" and miss["reference_answer"] and miss["key_idea"] and miss["answer"] == WRONG


def test_quiz_bonus_is_paid_once_per_question_and_repeats_earn_nothing(client):
    pid = "qz-xp"
    uid = _user(client, pid)
    s = _start(client, pid).json()
    qids = _qids(s["id"])
    for pos, qid in enumerate(qids):
        _answer(client, pid, s["id"], pos, _good(qid))
    first = client.get(f"/api/quiz/{s['id']}/results", headers=auth(pid=pid)).json()
    with SessionLocal() as db:
        bonus = {e.key: e.amount for e in db.query(XpEvent).filter_by(user_id=uid, kind="quiz")}
        answer_xp = sum(e.amount for e in db.query(XpEvent).filter_by(user_id=uid, kind="answer"))
    assert bonus == {f"quizq:{q}": 3 for q in qids}
    assert first["xp"] == answer_xp + 15 and first["score"] == 1.0 and first["new_best"]
    # A second quiz with the same questions pays nothing.
    with SessionLocal() as db:
        user = db.get(User, uid)
        again = quiz.start(db, user, scope="language", value="python", length=5, minutes=5, instant=False)
        again.question_ids = qids
        for slot in db.query(QuizAnswer).filter_by(quiz_id=again.id).all():
            slot.question_id = qids[slot.position]
        db.commit()
        again_id = again.id
    for pos, qid in enumerate(qids):
        _answer(client, pid, again_id, pos, _good(qid))
    second = client.get(f"/api/quiz/{again_id}/results", headers=auth(pid=pid)).json()
    assert second["xp"] == 0 and second["new_best"] is False and second["best_before"] == 1.0


def test_answers_already_right_before_the_quiz_get_no_bonus(client):
    pid = "qz-known"
    uid = _user(client, pid)
    s = _start(client, pid).json()
    qids = _qids(s["id"])
    r = client.post("/api/responses", json={"question_id": qids[0], "answer_text": _good(qids[0])}, headers=auth(pid=pid))
    assert r.status_code == 201
    _answer(client, pid, s["id"], 0, _good(qids[0]))
    _finish(client, pid, s["id"])
    with SessionLocal() as db:
        assert db.query(XpEvent).filter_by(user_id=uid, key=f"quizq:{qids[0]}").count() == 0


def test_beat_the_clock_needs_eighty_percent_on_ten_or_more(client):
    pid = "qz-beat"
    uid = _user(client, pid)
    s = _start(client, pid, length=5).json()
    for pos, qid in enumerate(_qids(s["id"])):
        _answer(client, pid, s["id"], pos, _good(qid))
    with SessionLocal() as db:
        assert db.query(UserBadge).filter_by(user_id=uid, badge="beat-the-clock").count() == 0  # 5/5 is too short
    s = _start(client, pid, scope="mixed", length=10, minutes=15).json()
    qids = _qids(s["id"])
    for pos, qid in enumerate(qids):
        _answer(client, pid, s["id"], pos, _good(qid) if pos < 8 else WRONG)
    res = client.get(f"/api/quiz/{s['id']}/results", headers=auth(pid=pid)).json()
    assert res["score"] == 0.8 and res["beat_the_clock"] is True
    with SessionLocal() as db:
        assert db.query(UserBadge).filter_by(user_id=uid, badge="beat-the-clock").count() == 1


def test_history_keeps_every_quiz_and_the_best_score_per_choice(client):
    pid = "qz-history"
    _user(client, pid)
    for right in (2, 4):
        s = _start(client, pid, scope="topic", value="debugging").json()
        for pos, qid in enumerate(_qids(s["id"])):
            _answer(client, pid, s["id"], pos, _good(qid) if pos < right else WRONG)
    s = _start(client, pid, scope="language", value="java").json()
    _finish(client, pid, s["id"])  # ended early with nothing answered
    h = client.get("/api/quiz/history", headers=auth(pid=pid)).json()
    assert h["total"] == 3 and [q["correct"] for q in h["quizzes"]] == [0, 4, 2]
    best = {b["scope_value"]: b for b in h["best"]}
    assert best["debugging"]["best_correct"] == 4 and best["debugging"]["attempts"] == 2
    assert best["debugging"]["scope_label"] == "Debugging" and best["java"]["best_score"] == 0.0


def test_purge_removes_quizzes_and_retries(client, monkeypatch):
    from app.api import admin as admin_mod

    token = "q" * 40
    monkeypatch.setattr(admin_mod, "get_settings", lambda: type("S", (), {"admin_token": token})())
    pid = "qz-purge"
    _user(client, pid)
    s = _start(client, pid).json()
    _answer(client, pid, s["id"], 0, _good(_qids(s["id"])[0]))
    client.post("/api/review/exercises/py-fizzbuzz/retry", headers=auth(pid=pid))
    dry = client.post("/api/admin/purge-users", json={"identities": [f"github:{pid}"]}, headers={"X-Admin-Token": token}).json()
    assert dry["users"][0]["quizzes"] == 1 and dry["users"][0]["review_retries"] == 1
    client.post("/api/admin/purge-users", json={"identities": [f"github:{pid}"], "dry_run": False}, headers={"X-Admin-Token": token})
    from app.models.models import ReviewRetry

    with SessionLocal() as db:
        live = {u for (u,) in db.query(User.id).all()}
        for model in (QuizSession, QuizAnswer, ReviewRetry):
            assert {u for (u,) in db.query(model.user_id).all()} <= live
