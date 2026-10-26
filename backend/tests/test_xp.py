"""XP, levels, badges and the leaderboard."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from app.content.exercises import BY_SLUG, EXERCISES
from app.db.session import SessionLocal
from app.models.models import (
    DailyCompletion,
    ExerciseAttempt,
    ExerciseHelp,
    Feedback,
    LearnerProfile,
    Question,
    Response,
    SkillDomain,
    User,
    UserBadge,
    XpEvent,
)
from app.services import xp
from tests.conftest import auth

UTC = timezone.utc


def _user(client, pid, **kw):
    client.get("/api/me", headers=auth(pid=pid, **kw))
    with SessionLocal() as db:
        return db.query(User).filter_by(provider_account_id=pid).one().id


def _question(db, *, difficulty="beginner", language=None, domain=None):
    q = db.query(Question).join(SkillDomain, SkillDomain.id == Question.domain_id)
    if language:
        q = q.filter(Question.language == language)
    if domain:
        q = q.filter(SkillDomain.slug == domain)
    return [x for x in q.all() if xp._diff(x.difficulty) == difficulty][0]


def _answer(db, uid, q, *, verdict="correct", hints=0, when=None, lang="en"):
    r = Response(user_id=uid, question_id=q.id, answer_text="because", created_at=when or datetime.now(UTC))
    db.add(r)
    db.flush()
    db.add(Feedback(response_id=r.id, overall_score=0.9, details={"verdict": verdict, "hints_used": hints, "answer_language": lang}))
    db.commit()


def _ex(language, difficulty="beginner"):
    return next(e for e in EXERCISES if e["language"] == language and e["difficulty"] == difficulty)


def _pass(db, uid, e, when=None):
    db.add(ExerciseAttempt(user_id=uid, slug=e["slug"], language=e["language"], passed=len(e["tests"]),
                           total=len(e["tests"]), code="x", created_at=when or datetime.now(UTC)))
    db.commit()


def _sync(uid, now=None):
    """Sync and return the new awards as plain (key, amount, retro) tuples and badge keys."""
    with SessionLocal() as db:
        res = xp.sync_user(db, db.get(User, uid), now)
        return [(e.key, e.amount, e.retro) for e in res.events], [b.badge for b in res.badges]


# ── Levels ────────────────────────────────────────────────────────────────


def test_levels_grow_and_have_brand_names():
    assert [xp.level_floor(n) for n in range(1, 6)] == [0, 100, 300, 600, 1000]
    assert xp.level_for(0) == 1 and xp.level_for(99) == 1 and xp.level_for(100) == 2 and xp.level_for(4500) == 10
    info = xp.level_info(150)
    assert info["level"] == 2 and info["level_name"] == "Tracer" and info["next_level_name"] == "Debugger"
    assert info["to_next"] == 150 and info["progress"] == 0.25
    assert xp.level_name(1) == "Initiate" and xp.level_name(9) == "Limit Breaker"
    assert xp.level_name(25) == "Limitless"


def test_there_are_twenty_badges_with_plain_descriptions():
    assert 12 <= len(xp.BADGES) <= 20
    assert len({b.key for b in xp.BADGES}) == len(xp.BADGES)
    for b in xp.BADGES:
        assert b.description.endswith(".") and len(b.description) < 90


# ── XP rules ──────────────────────────────────────────────────────────────


def test_correct_answers_scale_with_difficulty_and_hints_cost_a_little(client):
    uid = _user(client, "xp-rules")
    with SessionLocal() as db:
        beg = _question(db, difficulty="beginner")
        mid = _question(db, difficulty="intermediate")
        adv = _question(db, difficulty="advanced")
        ids = beg.id, mid.id, adv.id
        _answer(db, uid, beg, verdict="partially_correct")  # partial answers earn nothing
        _answer(db, uid, beg)
        _answer(db, uid, beg)  # the same question again doesn't pay twice
        _answer(db, uid, mid, hints=2)
        _answer(db, uid, adv, hints=5)  # the hint cut stops at 30%
    _sync(uid)
    with SessionLocal() as db:
        got = {e.key: e.amount for e in db.query(XpEvent).filter_by(user_id=uid)}
    assert got == {f"answer:{ids[0]}": 10, f"answer:{ids[1]}": 16, f"answer:{ids[2]}": 21}


def test_exercises_pay_more_and_help_reduces_it(client):
    uid = _user(client, "xp-ex")
    clean, hinted, helped = _ex("python"), _ex("javascript"), _ex("php", "intermediate")
    with SessionLocal() as db:
        _pass(db, uid, clean)
        db.add(ExerciseHelp(user_id=uid, slug=hinted["slug"], kind="hint", level=2, before_pass=1))
        db.add(ExerciseHelp(user_id=uid, slug=helped["slug"], kind="solution", level=0, before_pass=1))
        db.commit()
        _pass(db, uid, hinted)
        _pass(db, uid, helped)
        _pass(db, uid, clean)  # passing again doesn't pay twice
    _sync(uid)
    with SessionLocal() as db:
        got = {e.key: (e.amount, e.label) for e in db.query(XpEvent).filter_by(user_id=uid)}
        badges = {b.badge for b in db.query(UserBadge).filter_by(user_id=uid)}
    assert got[f"exercise:{clean['slug']}"][0] == 30
    assert got[f"exercise:{hinted['slug']}"][0] == 24  # 2 hints: -20%
    assert got[f"exercise:{helped['slug']}"] == (38, f"Passed: {helped['title']} (PHP), solved with help")  # 50 - 25%
    assert {"ex-python", "ex-javascript", "ex-php", "unassisted"} <= badges
    assert "polyglot" not in badges and "ex-cpp" not in badges


def test_daily_challenges_and_streak_bonuses(client):
    uid = _user(client, "xp-daily")
    with SessionLocal() as db:
        qid = db.query(Question.id).first()[0]
        for i, day in enumerate(["2026-10-01", "2026-10-02", "2026-10-03", "2026-10-05"]):
            db.add(DailyCompletion(user_id=uid, day=day, question_id=qid, score=0.5,
                                   created_at=datetime(2026, 10, 1 + i, 4, tzinfo=UTC)))
        db.commit()
    _sync(uid)
    with SessionLocal() as db:
        got = {e.key: e.amount for e in db.query(XpEvent).filter_by(user_id=uid)}
        badges = {b.badge for b in db.query(UserBadge).filter_by(user_id=uid)}
    assert sum(v for k, v in got.items() if k.startswith("daily:")) == 4 * xp.DAILY_XP
    assert got == {**{k: v for k, v in got.items() if k.startswith("daily:")}, "streak:2026-10-02": 5, "streak:2026-10-03": 10}
    assert {"daily-first", "streak-3"} <= badges and "streak-7" not in badges


def test_long_streak_bonus_is_capped_and_unlocks_streak_badges(client):
    uid = _user(client, "xp-streak30")
    start = datetime(2026, 8, 1, 4, tzinfo=UTC)
    with SessionLocal() as db:
        qid = db.query(Question.id).first()[0]
        for i in range(30):
            d = start + timedelta(days=i)
            db.add(DailyCompletion(user_id=uid, day=d.date().isoformat(), question_id=qid, score=1, created_at=d))
        db.commit()
    _sync(uid)
    with SessionLocal() as db:
        streak = [e.amount for e in db.query(XpEvent).filter_by(user_id=uid, kind="streak")]
        badges = {b.badge for b in db.query(UserBadge).filter_by(user_id=uid)}
    assert max(streak) == xp.STREAK_MAX and len(streak) == 29
    assert {"streak-3", "streak-7", "streak-30"} <= badges


def test_answer_badges_for_languages_topics_filipino_and_counts(client):
    uid = _user(client, "xp-badges")
    with SessionLocal() as db:
        _answer(db, uid, _question(db, language="cpp"))
        _answer(db, uid, _question(db, language="java", difficulty="intermediate"))
        _answer(db, uid, _question(db, domain="oop", difficulty="intermediate"))
        _answer(db, uid, _question(db, language="python"), lang="taglish")
        _answer(db, uid, _question(db, difficulty="advanced"))
    _sync(uid)
    with SessionLocal() as db:
        badges = {b.badge for b in db.query(UserBadge).filter_by(user_id=uid)}
    assert {"first-correct", "cpp-answer", "java-answer", "oop-answer", "filipino", "advanced"} <= badges
    assert "ten-correct" not in badges


def test_polyglot_needs_all_five_languages(client):
    uid = _user(client, "xp-poly")
    with SessionLocal() as db:
        for lang in xp.CODE_LANGUAGES:
            _pass(db, uid, _ex(lang))
    _sync(uid)
    with SessionLocal() as db:
        badges = {b.badge for b in db.query(UserBadge).filter_by(user_id=uid)}
    assert {"polyglot", *(f"ex-{lang}" for lang in xp.CODE_LANGUAGES)} <= badges


# ── Sync: retroactive and idempotent ──────────────────────────────────────


def test_sync_is_retroactive_idempotent_and_dated_by_the_activity(client):
    uid = _user(client, "xp-retro")
    old = datetime(2026, 9, 1, 2, tzinfo=UTC)
    with SessionLocal() as db:
        _answer(db, uid, _question(db), when=old)
    events, badges = _sync(uid)
    assert len(events) == 1 and events[0][2] == 1 and badges == ["first-correct"]
    assert _sync(uid) == ([], [])
    with SessionLocal() as db:
        e = db.query(XpEvent).filter_by(user_id=uid).one()
        assert xp._aware(e.created_at) == old
        _answer(db, uid, _question(db, difficulty="intermediate"))
    events, _ = _sync(uid)
    assert len(events) == 1 and events[0][2] == 0


def test_startup_backfill_runs_once_for_every_learner(client):
    from app import main
    from app.models.models import AppMeta

    uid = _user(client, "xp-backfill")
    with SessionLocal() as db:
        _answer(db, uid, _question(db))
        db.query(AppMeta).filter_by(key=main.XP_BACKFILL_KEY).delete()
        db.commit()
    main.backfill_xp()
    with SessionLocal() as db:
        assert db.query(XpEvent).filter_by(user_id=uid).count() == 1
        assert db.get(AppMeta, main.XP_BACKFILL_KEY).value == main.XP_BACKFILL_VERSION
        assert db.get(LearnerProfile, uid) is not None


# ── API ───────────────────────────────────────────────────────────────────


def test_xp_endpoint_shows_level_bar_and_all_badges(client):
    h = auth(pid="xp-api")
    uid = _user(client, "xp-api")
    with SessionLocal() as db:
        _answer(db, uid, _question(db, difficulty="advanced"))
    body = client.get("/api/xp", headers=h).json()
    assert body["xp"] == 30 and body["level"] == 1 and body["next_level_at"] == 100 and body["to_next"] == 70
    assert len(body["badges"]) == len(xp.BADGES)
    earned = {b["key"] for b in body["badges"] if b["earned"]}
    assert earned == {"first-correct", "advanced"} and body["badges_earned"] == 2
    assert body["recent"][0]["amount"] == 30


def test_answering_through_the_api_awards_xp_and_news_is_shown_once(client):
    h = auth(pid="xp-news")
    client.post("/api/xp/sync", headers=h)  # nothing yet
    with SessionLocal() as db:
        q = db.query(Question).filter(Question.rubric.isnot(None)).first()
        ref = (q.rubric or {}).get("reference_answer") or "x"
        accepted = (q.rubric or {}).get("accepted_answers") or []
    answer = accepted[0] if accepted else ref
    r = client.post("/api/responses", headers=h, json={"question_id": q.id, "answer_text": answer})
    assert r.status_code == 201
    news = client.post("/api/xp/sync", headers=h).json()["news"]
    assert r.json()["feedback"]["verdict"] == "correct"
    assert news["xp"] > 0 and news["badges"][0]["name"] == "First Build" and news["retro"] is False
    again = client.post("/api/xp/sync", headers=h).json()["news"]
    assert again == {"xp": 0, "retro": False, "items": [], "badges": []}


def test_passing_an_exercise_through_the_api_awards_xp(client):
    h = auth(pid="xp-ex-api")
    e = BY_SLUG[_ex("python")["slug"]]
    results = [{"output": json.dumps(t["expected"]), "error": None} for t in e["tests"]]
    assert client.post(f"/api/exercises/{e['slug']}/submit", headers=h, json={"code": "x", "results": results}).json()["solved"]
    news = client.post("/api/xp/sync", headers=h).json()["news"]
    assert news["xp"] == 30 and {b["key"] for b in news["badges"]} == {"ex-python", "unassisted"}


def test_leaderboard_never_shows_emails_or_real_names_by_default(client):
    _user(client, "lb-ana", name="Ana Reyes", email="ana.reyes@example.com")
    uid = _user(client, "lb-ana")
    with SessionLocal() as db:
        _answer(db, uid, _question(db, difficulty="advanced"))
    body = client.get("/api/leaderboard?period=all", headers=auth(pid="lb-ana", name="Ana Reyes", email="ana.reyes@example.com"))
    text = body.text
    assert "@" not in text and "ana.reyes" not in text and "Ana Reyes" not in text
    data = body.json()
    me = next(e for e in data["entries"] if e["is_you"])
    assert me["name"] == data["you"]["name"] and data["you"]["visibility"] == "handle"
    assert len(me["name"].split()) == 3  # e.g. "Swift Parser 42"


def test_visibility_settings_name_anonymous_and_hidden(client):
    h = auth(pid="lb-vis", name="Ben Cruz")
    uid = _user(client, "lb-vis", name="Ben Cruz")
    with SessionLocal() as db:
        for d in ("beginner", "intermediate", "advanced"):
            _answer(db, uid, _question(db, difficulty=d))
    prof = client.get("/api/xp/profile", headers=h).json()
    assert prof["visibility"] == "handle" and prof["name_available"] and prof["shown_as"] == prof["handle"]

    def mine():
        data = client.get("/api/leaderboard?period=all", headers=h).json()
        return next((e for e in data["entries"] if e["is_you"]), None), data["you"]

    assert client.put("/api/xp/profile", headers=h, json={"visibility": "name"}).json()["shown_as"] == "Ben Cruz"
    assert mine()[0]["name"] == "Ben Cruz"
    client.put("/api/xp/profile", headers=h, json={"visibility": "anonymous"})
    assert mine()[0]["name"] == "Anonymous learner"
    client.put("/api/xp/profile", headers=h, json={"visibility": "hidden"})
    entry, you = mine()
    assert entry is None and you["visibility"] == "hidden" and you["rank"] is not None
    assert client.put("/api/xp/profile", headers=h, json={"visibility": "everyone"}).status_code == 422
    old = client.put("/api/xp/profile", headers=h, json={"visibility": "handle"}).json()["handle"]
    assert client.post("/api/xp/profile/handle", headers=h).json()["handle"] != old


def test_email_like_display_names_are_never_shown(client):
    h = auth(pid="lb-mail", name="", email="secret.person@example.com")
    _user(client, "lb-mail", name="", email="secret.person@example.com")
    prof = client.put("/api/xp/profile", headers=h, json={"visibility": "name"}).json()
    assert "secret" not in json.dumps(prof)  # falls back to the handle
    assert prof["shown_as"] == prof["handle"]


def test_weekly_board_uses_manila_weeks_and_ranks_ties_together(client):
    # Monday 00:00 in Manila is Sunday 16:00 UTC.
    assert xp.week_start(datetime(2026, 10, 25, 16, 0, tzinfo=UTC)) == datetime(2026, 10, 25, 16, 0, tzinfo=UTC)
    assert xp.week_start(datetime(2026, 10, 25, 15, 59, tzinfo=UTC)) == datetime(2026, 10, 18, 16, 0, tzinfo=UTC)

    a, b, c = (_user(client, f"lb-week-{n}") for n in "abc")
    now = datetime.now(UTC)
    with SessionLocal() as db:
        q1, q2 = _question(db), _question(db, difficulty="intermediate")
        _answer(db, a, q2, when=now)
        _answer(db, b, q2, when=now)
        _answer(db, c, q1, when=xp.week_start(now) - timedelta(minutes=1))  # last week
    for uid in (a, b, c):
        _sync(uid)
    week = client.get("/api/leaderboard?period=week", headers=auth(pid="lb-week-c")).json()
    ranks = {e["xp"] for e in week["entries"]}
    assert week["you"]["xp"] == 0 and week["you"]["rank"] is None and "week_start" in week
    with SessionLocal() as db:
        ha, hb = db.get(LearnerProfile, a).handle, db.get(LearnerProfile, b).handle
    tied = [e for e in week["entries"] if e["name"] in (ha, hb)]
    assert len(tied) == 2 and tied[0]["rank"] == tied[1]["rank"] and 20 in ranks
    alltime = client.get("/api/leaderboard?period=all", headers=auth(pid="lb-week-c")).json()
    assert alltime["you"]["xp"] == 10 and alltime["you"]["rank"] is not None


def test_leaderboard_lists_at_most_fifty(client):
    with SessionLocal() as db:
        q = _question(db)
    ids = [_user(client, f"lb-many-{i}") for i in range(55)]
    with SessionLocal() as db:
        for uid in ids:
            _answer(db, uid, q)
    for uid in ids:
        _sync(uid)
    data = client.get("/api/leaderboard?period=all", headers=auth(pid="lb-many-54")).json()
    assert len(data["entries"]) == xp.LEADERBOARD_SIZE and data["ranked"] >= 55
    assert data["you"]["rank"] is not None


@pytest.mark.parametrize("path", ["/api/xp", "/api/leaderboard", "/api/xp/profile"])
def test_xp_endpoints_need_sign_in(client, path):
    assert client.get(path).status_code == 401


def test_first_visit_requests_at_the_same_time_share_one_profile(client):
    """The header and the page both sync on a first visit; neither may fail."""
    import threading

    uid = _user(client, "xp-race")
    with SessionLocal() as db:
        _answer(db, uid, _question(db))
    errors, barrier = [], threading.Barrier(4)

    def go():
        try:
            barrier.wait()
            with SessionLocal() as db:
                xp.sync_user(db, db.get(User, uid))
                xp.summary(db, db.get(User, uid))
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=go) for _ in range(4)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not errors
    with SessionLocal() as db:
        assert db.query(LearnerProfile).filter_by(user_id=uid).count() == 1
        assert db.query(XpEvent).filter_by(user_id=uid).count() == 1
