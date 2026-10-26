"""Learning paths: definitions, progress from history, unlocking, skip ahead, the step picker and XP."""

from datetime import datetime, timedelta, timezone

from app.content.exercises import BY_SLUG as EXERCISES
from app.content.paths import ALL_LEVELS, PASS_MARK, PATHS, exercise_slugs
from app.db.session import SessionLocal
from app.models.models import ExerciseAttempt, Feedback, PathActivity, PathSkip, Response, User, XpEvent
from app.services import paths, xp
from tests.conftest import auth

UTC = timezone.utc


def _user(client, pid):
    client.get("/api/me", headers=auth(pid=pid))
    with SessionLocal() as db:
        return db.query(User).filter_by(provider_account_id=pid).one().id


def _pool(slug, number):
    step = paths.get_path(slug).steps[number - 1]
    with SessionLocal() as db:
        return paths.pool_ids(step, paths._catalog(db))


def _answer(uid, qids, score=0.9, when=None):
    with SessionLocal() as db:
        for qid in qids:
            r = Response(user_id=uid, question_id=qid, answer_text="because", created_at=when or datetime.now(UTC))
            db.add(r)
            db.flush()
            db.add(Feedback(response_id=r.id, overall_score=score,
                            details={"verdict": "correct" if score >= 0.7 else "partial", "hints_used": 0}))
        db.commit()


def _pass(uid, slug, when=None):
    e = EXERCISES[slug]
    with SessionLocal() as db:
        db.add(ExerciseAttempt(user_id=uid, slug=slug, language=e["language"], passed=len(e["tests"]),
                               total=len(e["tests"]), code="x", created_at=when or datetime.now(UTC)))
        db.commit()


def _detail(client, pid, slug):
    r = client.get(f"/api/paths/{slug}", headers=auth(pid=pid))
    assert r.status_code == 200
    return r.json()


# ── Definitions ───────────────────────────────────────────────────────────


def test_paths_cover_the_requested_subjects_with_real_content(client):
    assert [p.slug for p in PATHS] == ["fundamentals", "web", "python", "javascript", "cpp", "java", "php", "oop", "logic"]
    order = list(ALL_LEVELS)
    with SessionLocal() as db:
        catalog = paths._catalog(db)
    for p in PATHS:
        assert 4 <= len(p.steps) <= 7 and p.blurb and len({s.key for s in p.steps}) == len(p.steps)
        # Beginner to advanced.
        assert order.index(p.steps[0].levels[0]) == 0 and order.index(p.steps[-1].levels[-1]) == 2
        for s in p.steps:
            pool = paths.pool_ids(s, catalog)
            assert len(pool) >= s.questions, (p.slug, s.key, len(pool))
            if s.exercise:
                assert exercise_slugs(s.exercise), (p.slug, s.key)
    assert exercise_slugs("any:sum-list") == ["py-sum-list", "js-sum-array", "cpp-sum-list", "java-sum-list", "php-sum-list"]
    assert 0.7 <= PASS_MARK <= 0.8


def test_paths_need_sign_in(client):
    assert client.get("/api/paths").status_code == 401
    assert client.get("/api/paths/python").status_code == 401


def test_unknown_path_or_step_is_404(client):
    h = auth(pid="paths-404")
    assert client.get("/api/paths/cobol", headers=h).status_code == 404
    assert client.get("/api/paths/python/steps/0/next", headers=h).status_code == 404
    assert client.get("/api/paths/python/steps/99/next", headers=h).status_code == 404
    assert client.post("/api/paths/python/steps/99/skip-ahead", headers=h).status_code == 404


# ── Progress and unlocking ────────────────────────────────────────────────


def test_new_learner_starts_with_step_one_open_and_nothing_to_continue(client):
    _user(client, "paths-new")
    body = client.get("/api/paths", headers=auth(pid="paths-new")).json()
    assert len(body["paths"]) == 9 and body["continue"] is None
    assert body["pass_mark"] == PASS_MARK and body["step_xp"] == 25 and body["path_xp"] == 100
    assert all(p["steps_done"] == 0 and p["progress"] == 0 and not p["started"] for p in body["paths"])
    steps = _detail(client, "paths-new", "python")["steps"]
    assert [s["status"] for s in steps] == ["open"] + ["locked"] * 6
    assert steps[0]["exercise"]["options"][0]["slug"] == "py-sum-list" and not steps[0]["exercise"]["any_language"]


def test_existing_answers_count_and_unlock_the_next_step(client):
    uid = _user(client, "paths-history")
    _answer(uid, _pool("python", 1)[:4], score=0.9, when=datetime.now(UTC) - timedelta(days=3))
    steps = _detail(client, "paths-history", "python")["steps"]
    first = steps[0]
    assert first["answered"] == 4 and first["score"] == 0.9 and first["questions_passed"]
    assert first["status"] == "open"  # its exercise isn't passed yet, so it isn't done
    assert steps[1]["status"] == "open" and steps[2]["status"] == "locked"
    _pass(uid, "py-sum-list")
    steps = _detail(client, "paths-history", "python")["steps"]
    assert steps[0]["status"] == "done" and steps[0]["exercise"]["passed"]


def test_low_scores_keep_the_next_step_locked(client):
    uid = _user(client, "paths-low")
    _answer(uid, _pool("web", 1)[:4], score=0.6)
    steps = _detail(client, "paths-low", "web")["steps"]
    assert steps[0]["score"] == 0.6 and not steps[0]["questions_passed"] and steps[1]["status"] == "locked"
    # The step score is the average of the best answers, so retrying a question can lift it.
    _answer(uid, _pool("web", 1)[:2], score=1.0)
    steps = _detail(client, "paths-low", "web")["steps"]
    assert steps[0]["score"] == 0.8 and steps[0]["status"] == "done" and steps[1]["status"] == "open"


def test_unanswered_questions_count_as_zero(client):
    uid = _user(client, "paths-few")
    _answer(uid, _pool("logic", 1)[:2], score=1.0)
    step = _detail(client, "paths-few", "logic")["steps"][0]
    assert step["answered"] == 2 and step["target"] == 4 and step["score"] == 0.5 and step["status"] == "open"


def test_a_passed_exercise_alone_unlocks_the_next_step(client):
    uid = _user(client, "paths-exercise")
    _pass(uid, "java-sum-list")
    steps = _detail(client, "paths-exercise", "java")["steps"]
    assert steps[0]["status"] == "open" and steps[0]["exercise"]["passed"] and steps[1]["status"] == "open"


def test_any_language_exercise_accepts_whichever_language_passed(client):
    uid = _user(client, "paths-any")
    _pass(uid, "php-fizzbuzz")
    step = _detail(client, "paths-any", "fundamentals")["steps"][2]
    assert step["exercise"]["any_language"] and step["exercise"]["passed_slug"] == "php-fizzbuzz"
    assert {o["language"] for o in step["exercise"]["options"]} == {"python", "javascript", "cpp", "java", "php"}


def test_skip_ahead_opens_a_locked_step_and_says_so(client):
    _user(client, "paths-skip")
    h = auth(pid="paths-skip")
    body = client.post("/api/paths/cpp/steps/4/skip-ahead", headers=h).json()
    steps = body["steps"]
    assert steps[3]["status"] == "open" and steps[3]["skipped"]
    assert steps[1]["status"] == "locked" and not steps[1]["skipped"]
    client.post("/api/paths/cpp/steps/4/skip-ahead", headers=h)  # twice is fine
    with SessionLocal() as db:
        uid = db.query(User.id).filter_by(provider_account_id="paths-skip").scalar()
        assert db.query(PathSkip).filter_by(user_id=uid).count() == 1
    cont = client.get("/api/paths", headers=h).json()["continue"]
    assert cont["path"]["slug"] == "cpp" and cont["step"]["number"] == 4 and not cont["from_history"]


def test_skip_note_goes_away_once_the_step_is_unlocked_normally(client):
    uid = _user(client, "paths-skip-later")
    client.post("/api/paths/python/steps/2/skip-ahead", headers=auth(pid="paths-skip-later"))
    _pass(uid, "py-sum-list")
    step = _detail(client, "paths-skip-later", "python")["steps"][1]
    assert step["status"] == "open" and not step["skipped"]


# ── The step picker reuses the engine and grader ──────────────────────────


def test_step_questions_come_from_the_step_and_are_graded_as_usual(client):
    uid = _user(client, "paths-picker")
    h = auth(pid="paths-picker")
    pool = set(_pool("javascript", 3))
    seen = []
    for _ in range(3):
        q = client.get(f"/api/paths/javascript/steps/3/next?exclude={','.join(map(str, seen))}", headers=h).json()
        assert q["id"] in pool and q["id"] not in seen and q["language"] == "javascript"
        seen.append(q["id"])
    r = client.post("/api/responses", json={"question_id": seen[0], "answer_text": "It prints each value because the loop runs to the end."}, headers=h)
    assert r.status_code == 201
    step = _detail(client, "paths-picker", "javascript")["steps"][2]
    assert step["answered"] == 1
    with SessionLocal() as db:
        act = db.query(PathActivity).filter_by(user_id=uid, path="javascript").one()
        assert act.step == "decisions-loops"


def test_picker_prefers_questions_not_answered_well_yet(client):
    uid = _user(client, "paths-weak")
    pool = _pool("logic", 5)  # two questions
    _answer(uid, [pool[0]], score=1.0)
    for _ in range(5):
        q = client.get("/api/paths/logic/steps/5/next", headers=auth(pid="paths-weak")).json()
        assert q["id"] == pool[1]


def test_picker_follows_mastery_inside_the_step_levels(client):
    uid = _user(client, "paths-level")
    with SessionLocal() as db:
        user = db.get(User, uid)
        p = paths.get_path("python")
        for _ in range(6):
            q = paths.next_question(db, user, p, 1)
            assert q.difficulty == "beginner"  # step 1 is beginner-only, whatever the mastery


# ── Continue ──────────────────────────────────────────────────────────────


def test_continue_comes_from_history_when_no_path_was_opened(client):
    uid = _user(client, "paths-continue")
    _answer(uid, _pool("oop", 1)[:4], score=0.95)
    cont = client.get("/api/paths", headers=auth(pid="paths-continue")).json()["continue"]
    assert cont["from_history"] and cont["path"]["slug"] == "oop" and cont["step"]["number"] == 2


def test_continue_follows_the_last_opened_path(client):
    _user(client, "paths-last")
    h = auth(pid="paths-last")
    client.get("/api/paths/web/steps/1/next", headers=h)
    client.get("/api/paths/php/steps/1/next", headers=h)
    cont = client.get("/api/paths", headers=h).json()["continue"]
    assert cont["path"]["slug"] == "php" and cont["step"]["title"] == "First steps"


# ── XP and badges ─────────────────────────────────────────────────────────


def _finish_fundamentals(uid, when=None):
    for n in range(1, 5):
        _answer(uid, _pool("fundamentals", n), score=0.9, when=when)
    for slug in ("py-sum-list", "java-reverse-string", "js-fizzbuzz", "cpp-largest"):
        _pass(uid, slug, when=when)


def test_finishing_steps_and_a_path_earns_xp_and_badges(client):
    uid = _user(client, "paths-xp")
    with SessionLocal() as db:
        xp.sync_user(db, db.get(User, uid))  # an existing learner, profile already made
    _finish_fundamentals(uid)
    with SessionLocal() as db:
        res = xp.sync_user(db, db.get(User, uid))
        got = {e.key: (e.amount, e.retro) for e in res.events}
        badges = {b.badge for b in res.badges}
    for key in ("values-and-steps", "first-algorithms", "conditions-loops", "think-like-a-computer"):
        assert got[f"path-step:fundamentals:{key}"] == (paths.STEP_XP, 0)
    assert got["path:fundamentals"] == (paths.PATH_XP, 0)
    assert {"path-step", "path-finisher"} <= badges and "path-three" not in badges
    detail = _detail(client, "paths-xp", "fundamentals")
    assert detail["finished"] and detail["steps_done"] == 4 and detail["progress"] == 1.0
    # Syncing again adds nothing, and the badges show on the badges page.
    with SessionLocal() as db:
        assert xp.sync_user(db, db.get(User, uid)).events == []
    listed = {b["key"]: b for b in client.get("/api/xp", headers=auth(pid="paths-xp")).json()["badges"]}
    assert listed["path-finisher"]["earned"] and listed["path-finisher"]["group"] == "paths"
    assert not listed["path-three"]["earned"]


def test_path_xp_for_work_before_paths_existed_counts_as_past_work(client):
    uid = _user(client, "paths-retro")
    with SessionLocal() as db:
        xp.sync_user(db, db.get(User, uid))
    _finish_fundamentals(uid, when=datetime.now(UTC) - timedelta(days=40))
    with SessionLocal() as db:
        res = xp.sync_user(db, db.get(User, uid))
        path_events = [e for e in res.events if e.kind in xp.PATH_KINDS]
        assert path_events and all(e.retro == 1 for e in path_events)
        assert all(e.retro == 0 for e in res.events if e.kind not in xp.PATH_KINDS)
        assert {b.badge: b.retro for b in res.badges}["path-finisher"] == 1


def test_three_paths_earn_wayfinder(client):
    uid = _user(client, "paths-three")
    for slug in ("fundamentals", "logic", "web"):
        for n, step in enumerate(paths.get_path(slug).steps, start=1):
            _answer(uid, _pool(slug, n), score=0.9)
            if step.exercise:
                _pass(uid, exercise_slugs(step.exercise)[0])
    with SessionLocal() as db:
        res = xp.sync_user(db, db.get(User, uid))
        assert "path-three" in {b.badge for b in res.badges}
        assert db.query(XpEvent).filter(XpEvent.user_id == uid, XpEvent.kind == "path").count() == 3


def test_partial_progress_never_reaches_one_hundred_percent(client):
    uid = _user(client, "paths-partial")
    for n in range(1, 8):
        _answer(uid, _pool("python", n), score=0.9)  # every question, but no exercises
    d = _detail(client, "paths-partial", "python")
    assert d["steps_done"] == 1 and not d["finished"] and d["progress"] < 1.0  # only "Classes" has no exercise
