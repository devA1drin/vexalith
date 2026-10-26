"""Mistake review: items from history, filters, retries that fix, re-surfacing, XP and the badge."""

from datetime import datetime, timedelta, timezone

import pytest

from app.content.exercises import BY_SLUG as EXERCISES
from app.db.session import SessionLocal
from app.models.models import (
    AppMeta,
    ExerciseAttempt,
    ExerciseHelp,
    Feedback,
    Question,
    Response,
    ReviewRetry,
    SkillDomain,
    User,
    UserBadge,
    XpEvent,
)
from app.services import review, xp
from tests.conftest import auth


@pytest.fixture(autouse=True, scope="module")
def _off_the_leaderboard():
    """These learners earn XP this week; hide them afterwards so they don't crowd the board tests."""
    yield
    from app.models.models import LearnerProfile

    with SessionLocal() as db:
        for prof in (db.query(LearnerProfile).join(User, User.id == LearnerProfile.user_id)
                     .filter(User.provider_account_id.like("rv-%"))):
            prof.visibility = "hidden"
        db.commit()

UTC = timezone.utc
WRONG = "I am not sure what it does at all"


def _user(client, pid):
    client.get("/api/me", headers=auth(pid=pid))
    with SessionLocal() as db:
        return db.query(User).filter_by(provider_account_id=pid).one().id


def _questions(n, **filters):
    with SessionLocal() as db:
        q = db.query(Question).join(SkillDomain).filter(Question.source == "seed")
        for k, v in filters.items():
            q = q.filter(SkillDomain.slug == v) if k == "domain" else q.filter(getattr(Question, k) == v)
        return [x.id for x in q.order_by(Question.id).limit(n).all()]


def _good(qid):
    with SessionLocal() as db:
        r = db.get(Question, qid).rubric
        return (r.get("accepted_answers") or [None])[0] if r.get("kind") == "fill_blank" else r["reference_answer"]


def _log(uid, qid, verdict, when, text="because it loops", score=None):
    """Write an answer straight into history (as if graded) at a chosen time."""
    with SessionLocal() as db:
        r = Response(user_id=uid, question_id=qid, answer_text=text, created_at=when)
        db.add(r)
        db.flush()
        db.add(Feedback(
            response_id=r.id, overall_score=score if score is not None else (0.9 if verdict == "correct" else 0.3),
            misconceptions=[{"name": "early exit", "explanation": "The loop stops at the first match.", "evidence_span": ""}]
            if verdict != "correct" else [],
            raw_explanation="Close, but not quite.", details={"verdict": verdict, "missed_concepts": []},
        ))
        db.commit()


def _retry(uid, key, when):
    with SessionLocal() as db:
        db.add(ReviewRetry(user_id=uid, item=key, created_at=when))
        db.commit()


def _page(uid, now=None, **filters):
    with SessionLocal() as db:
        return review.page(db, db.get(User, uid), now=now, **filters)


def _post(client, pid, qid, text):
    r = client.post("/api/responses", json={"question_id": qid, "answer_text": text}, headers=auth(pid=pid))
    assert r.status_code == 201, r.text
    return r.json()


def _xp(uid):
    with SessionLocal() as db:
        return {e.key: e.amount for e in db.query(XpEvent).filter_by(user_id=uid)}


def test_review_needs_sign_in(client):
    assert client.get("/api/review").status_code == 401
    assert client.post("/api/review/exercises/py-fizzbuzz/retry").status_code == 401


def test_new_learner_has_an_empty_list(client):
    _user(client, "rv-empty")
    r = client.get("/api/review", headers=auth(pid="rv-empty"))
    assert r.status_code == 200
    d = r.json()
    assert d["items"] == [] and d["counts"]["to_fix"] == 0 and d["fixes"] == 0
    assert d["rules"] == {"fix_xp": 5, "confirm_days": 3, "second_look": 10}


def test_wrong_and_partly_right_answers_are_listed_from_existing_history(client):
    uid = _user(client, "rv-history")
    a, b, c = _questions(3, language="python")
    now = datetime.now(UTC)
    _log(uid, a, "incorrect", now - timedelta(days=5), text="it prints 10")
    _log(uid, b, "partially_correct", now - timedelta(days=4))
    _log(uid, c, "correct", now - timedelta(days=3))
    d = client.get("/api/review", headers=auth(pid="rv-history")).json()
    by_id = {i["id"]: i for i in d["items"]}
    assert set(by_id) == {a, b}
    assert by_id[a]["reason_label"] == "Wrong answer" and by_id[b]["reason_label"] == "Partly right"
    item = by_id[a]
    assert item["status"] == "to_fix" and item["last_answer"] == "it prints 10" and item["times_wrong"] == 1
    assert item["feedback"] == "The loop stops at the first match."  # the short feedback, not a walkthrough
    with SessionLocal() as db:
        assert item["explanation"] and item["explanation"] in " ".join(db.get(Question, a).rubric["hints"])
    assert d["counts"]["to_fix"] == 2 and d["items"][0]["id"] == b  # newest first


def test_a_correct_retry_from_review_fixes_it_and_pays_five_xp_once(client):
    pid = "rv-fix"
    uid = _user(client, pid)
    (qid,) = _questions(1, language="javascript")
    _post(client, pid, qid, WRONG)
    assert [i["id"] for i in client.get("/api/review", headers=auth(pid=pid)).json()["items"]] == [qid]
    assert client.post(f"/api/review/questions/{qid}/retry", headers=auth(pid=pid)).status_code == 201
    _post(client, pid, qid, _good(qid))
    d = client.get("/api/review", headers=auth(pid=pid)).json()
    assert d["items"] == [] and d["counts"]["waiting"] == 1 and d["fixes"] == 1
    assert d["coming_back"][0]["key"] == f"q:{qid}"
    assert _xp(uid)[f"fix:q:{qid}"] == 5
    # Getting it wrong again puts it back on the list, but fixing it again pays nothing more.
    _post(client, pid, qid, WRONG)
    assert client.get("/api/review", headers=auth(pid=pid)).json()["counts"]["to_fix"] == 1
    client.post(f"/api/review/questions/{qid}/retry", headers=auth(pid=pid))
    _post(client, pid, qid, _good(qid))
    with SessionLocal() as db:
        assert db.query(XpEvent).filter_by(user_id=uid, kind="fix").count() == 1


def test_wrong_then_right_without_review_leaves_the_list_but_earns_no_fix_xp(client):
    pid = "rv-farm"
    uid = _user(client, pid)
    (qid,) = _questions(1, language="php")
    _post(client, pid, qid, WRONG)
    _post(client, pid, qid, _good(qid))
    d = client.get("/api/review", headers=auth(pid=pid)).json()
    assert d["items"] == [] and d["fixes"] == 0
    assert not any(k.startswith("fix:") for k in _xp(uid))


def test_fixed_items_come_back_once_after_three_days_to_check_they_stuck(client):
    uid = _user(client, "rv-resurface")
    a, b = _questions(2, language="cpp")
    t0 = datetime.now(UTC) - timedelta(days=10)
    for q in (a, b):
        _log(uid, q, "incorrect", t0)
        _retry(uid, f"q:{q}", t0 + timedelta(minutes=1))
        _log(uid, q, "correct", t0 + timedelta(minutes=2))
    # A right answer before the check is due doesn't count as the check.
    _log(uid, b, "correct", t0 + timedelta(days=1))
    assert {i["id"] for i in _page(uid, now=t0 + timedelta(days=2))["items"]} == set()
    later = _page(uid, now=t0 + timedelta(days=3, minutes=5))
    assert {i["id"]: i["status"] for i in later["items"]} == {a: "check_again", b: "check_again"}
    assert later["counts"]["check_again"] == 2
    # Right again on the check: it stuck and leaves for good. Wrong on the check: back to "To fix".
    _log(uid, a, "correct", t0 + timedelta(days=4))
    _log(uid, b, "incorrect", t0 + timedelta(days=4))
    final = _page(uid, now=t0 + timedelta(days=9))
    assert {i["id"]: i["status"] for i in final["items"]} == {b: "to_fix"}
    assert final["counts"]["done"] == 1


def test_filters_by_topic_language_path_difficulty_and_kind(client):
    pid = "rv-filters"
    uid = _user(client, pid)
    py = _questions(2, language="python", domain="debugging")
    java = _questions(1, language="java", difficulty="advanced")
    now = datetime.now(UTC) - timedelta(hours=1)
    for q in py + java:
        _log(uid, q, "incorrect", now)
    e = EXERCISES["py-fizzbuzz"]
    with SessionLocal() as db:
        db.add(ExerciseAttempt(user_id=uid, slug="py-fizzbuzz", language="python", passed=1, total=len(e["tests"]), code="x", created_at=now))
        db.commit()
    h = auth(pid=pid)
    d = client.get("/api/review", headers=h).json()
    assert d["counts"]["shown"] == 4
    assert {o["value"] for o in d["filters"]["languages"]} == {"python", "java"}
    assert {o["value"] for o in d["filters"]["difficulties"]} <= {"beginner", "intermediate", "advanced"}
    assert "python" in {o["value"] for o in d["filters"]["paths"]}
    assert {i["id"] for i in client.get("/api/review?language=java", headers=h).json()["items"]} == set(java)
    assert {i["id"] for i in client.get("/api/review?topic=debugging", headers=h).json()["items"]} == set(py)
    assert all(i["difficulty"] == "advanced" for i in client.get("/api/review?difficulty=advanced", headers=h).json()["items"])
    assert [i["slug"] for i in client.get("/api/review?kind=exercise", headers=h).json()["items"]] == ["py-fizzbuzz"]
    in_path = client.get("/api/review?path=python", headers=h).json()["items"]
    assert in_path and all("python" in i["paths"] for i in in_path)
    assert client.get("/api/review?topic=../x", headers=h).status_code == 422


def test_failed_exercises_are_fixed_by_a_full_pass(client):
    pid = "rv-ex-failed"
    uid = _user(client, pid)
    e = EXERCISES["js-fizzbuzz"]
    n = len(e["tests"])
    t0 = datetime.now(UTC) - timedelta(hours=2)
    with SessionLocal() as db:
        db.add(ExerciseAttempt(user_id=uid, slug="js-fizzbuzz", language="javascript", passed=1, total=n, code="function f(){}", created_at=t0))
        db.commit()
    item = _page(uid)["items"][0]
    assert item["kind"] == "exercise" and item["reason_label"] == "Tests failing"
    assert item["feedback"] == f"1 of {n} tests passed." and item["last_answer"] == "function f(){}" and item["explanation"]
    _retry(uid, "x:js-fizzbuzz", t0 + timedelta(minutes=1))
    with SessionLocal() as db:
        # Failing runs while working on it don't push the retry out of the window.
        db.add(ExerciseAttempt(user_id=uid, slug="js-fizzbuzz", language="javascript", passed=2, total=n, code="x", created_at=t0 + timedelta(minutes=2)))
        db.add(ExerciseAttempt(user_id=uid, slug="js-fizzbuzz", language="javascript", passed=n, total=n, code="x", created_at=t0 + timedelta(minutes=3)))
        db.commit()
    d = _page(uid)
    assert d["items"] == [] and d["fixes"] == 1


def test_solved_with_help_needs_a_fresh_solve_after_retry(client):
    pid = "rv-ex-help"
    uid = _user(client, pid)
    e = EXERCISES["py-fizzbuzz"]
    n = len(e["tests"])
    t0 = datetime.now(UTC) - timedelta(hours=3)
    with SessionLocal() as db:
        db.add(ExerciseHelp(user_id=uid, slug="py-fizzbuzz", kind="solution", level=0, before_pass=1, created_at=t0))
        db.add(ExerciseAttempt(user_id=uid, slug="py-fizzbuzz", language="python", passed=n, total=n, code="sol", created_at=t0 + timedelta(minutes=1)))
        # Running the same code again isn't a fix.
        db.add(ExerciseAttempt(user_id=uid, slug="py-fizzbuzz", language="python", passed=n, total=n, code="sol", created_at=t0 + timedelta(minutes=2)))
        db.commit()
    (item,) = _page(uid)["items"]
    assert item["reason_label"] == "Solved with help" and item["status"] == "to_fix"
    r = client.post("/api/review/exercises/py-fizzbuzz/retry", headers=auth(pid=pid))
    assert r.status_code == 201
    with SessionLocal() as db:
        db.add(ExerciseAttempt(user_id=uid, slug="py-fizzbuzz", language="python", passed=n, total=n, code="mine",
                               created_at=datetime.now(UTC) + timedelta(seconds=1)))
        db.commit()
    assert _page(uid)["items"] == []
    assert client.post("/api/review/exercises/no-such-thing/retry", headers=auth(pid=pid)).status_code == 404
    assert client.post("/api/review/questions/999999/retry", headers=auth(pid=pid)).status_code == 404


def test_second_look_badge_after_ten_fixes(client):
    uid = _user(client, "rv-badge")
    qids = _questions(10, language="general")
    t0 = datetime.now(UTC) - timedelta(days=1)
    for i, q in enumerate(qids):
        _log(uid, q, "incorrect", t0 + timedelta(minutes=i))
        _retry(uid, f"q:{q}", t0 + timedelta(hours=1, minutes=i))
        if i < 9:
            _log(uid, q, "correct", t0 + timedelta(hours=1, minutes=i, seconds=30))
    with SessionLocal() as db:
        xp.sync_user(db, db.get(User, uid))
        assert db.query(UserBadge).filter_by(user_id=uid, badge="second-look").count() == 0
    _log(uid, qids[9], "correct", t0 + timedelta(hours=2))
    with SessionLocal() as db:
        res = xp.sync_user(db, db.get(User, uid))
        assert "second-look" in [b.badge for b in res.badges]
        assert sum(e.amount for e in db.query(XpEvent).filter_by(user_id=uid, kind="fix")) == 50


def test_fixes_made_before_review_launched_count_as_past_work(client):
    uid = _user(client, "rv-retro")
    (qid,) = _questions(1, language="html")
    t0 = datetime.now(UTC) - timedelta(days=30)
    with SessionLocal() as db:
        xp.sync_user(db, db.get(User, uid))  # a known learner (not their first sync)
    _log(uid, qid, "incorrect", t0)
    _retry(uid, f"q:{qid}", t0 + timedelta(minutes=1))
    _log(uid, qid, "correct", t0 + timedelta(minutes=2))
    with SessionLocal() as db:
        xp.mark_launch(db, xp.REVIEW_LAUNCH_KEY)
        assert db.get(AppMeta, xp.REVIEW_LAUNCH_KEY) is not None
        res = xp.sync_user(db, db.get(User, uid))
        fix = [e for e in res.events if e.kind == "fix"]
        assert fix and fix[0].retro == 1


def test_review_badges_sit_outside_the_core_twenty(client):
    assert len(xp.BADGES) == 20
    keys = {b.key for b in xp.REVIEW_BADGES}
    assert keys == {"second-look", "beat-the-clock"} and keys <= set(xp.BADGE_BY_KEY)
    for b in xp.REVIEW_BADGES:
        assert b.group == "review" and b.description.endswith(".") and len(b.description) < 90
