"""Daily challenge (determinism, Manila dates, streaks), safe migration and Progress v2."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import DailyCompletion, Question, User
from app.services import daily
from app.services.learning import get_progress, submit_response
from app.services.question_bank import SCHEMA_VERSION, migrate_schema, seed_domains_and_questions
from tests.conftest import auth

UTC = timezone.utc


def _user(client, pid):
    client.get("/api/me", headers=auth(pid=pid))
    with SessionLocal() as db:
        return db.query(User).filter_by(provider_account_id=pid).one().id


# ── Manila dates ──────────────────────────────────────────────────────────


def test_manila_day_boundaries():
    # Manila is UTC+8: 15:59 UTC is still the same day, 16:00 UTC is the next.
    assert daily.manila_today(datetime(2026, 10, 22, 15, 59, tzinfo=UTC)) == date(2026, 10, 22)
    assert daily.manila_today(datetime(2026, 10, 22, 16, 0, tzinfo=UTC)) == date(2026, 10, 23)
    # Early UTC morning of the 22nd is already afternoon in Manila.
    assert daily.manila_today(datetime(2026, 10, 21, 23, 0, tzinfo=UTC)) == date(2026, 10, 22)
    assert daily.next_reset(datetime(2026, 10, 22, 3, 0, tzinfo=UTC)) == datetime(2026, 10, 22, 16, 0, tzinfo=UTC)


# ── Deterministic pick ────────────────────────────────────────────────────


def test_daily_pick_is_deterministic_and_the_same_for_everyone(client):
    day = date(2026, 10, 22)
    with SessionLocal() as a, SessionLocal() as b:
        assert daily.pick_for(a, day).question.id == daily.pick_for(b, day).question.id
        assert all(daily.pick_for(a, day).question.id == daily.pick_for(a, day).question.id for _ in range(5))
    r1 = client.get("/api/daily").json()
    r2 = client.get("/api/daily").json()
    assert r1 == r2 and r1["timezone"] == "Asia/Manila"
    assert r1["date"] == daily.manila_today().isoformat()


def test_daily_rotates_languages_and_skills():
    start = date(2026, 3, 1)
    with SessionLocal() as db:
        picks = [daily.pick_for(db, start + timedelta(days=i)) for i in range(28)]
    week = [p.question.language for p in picks[:7]]
    assert len(set(week)) == 7  # a different language every day of the week
    assert all(picks[i].question.language != picks[i + 1].question.language for i in range(27))
    # The same language comes back a week later on a different skill.
    assert picks[0].question.language == picks[7].question.language
    assert picks[0].domain.slug != picks[7].domain.slug
    assert len({p.question.id for p in picks}) == 28


# ── Streaks ───────────────────────────────────────────────────────────────


def test_streak_calculation():
    t = date(2026, 10, 22)
    d = lambda n: t - timedelta(days=n)  # noqa: E731
    assert daily.streaks(set(), t) == (0, 0)
    assert daily.streaks({t}, t) == (1, 1)
    assert daily.streaks({d(1), d(2)}, t) == (2, 2)  # yesterday still counts until midnight
    assert daily.streaks({d(2), d(3)}, t) == (0, 2)  # missed yesterday: broken
    assert daily.streaks({t, d(1), d(2), d(5), d(6), d(7), d(8)}, t) == (3, 4)


def test_streak_uses_manila_dates_across_midnight(client):
    uid = _user(client, "daily-tz")
    # 15:30 UTC on Oct 21 = 23:30 Manila Oct 21; 16:30 UTC = 00:30 Manila Oct 22.
    late = datetime(2026, 10, 21, 15, 30, tzinfo=UTC)
    after_midnight = datetime(2026, 10, 21, 16, 30, tzinfo=UTC)
    with SessionLocal() as db:
        user = db.get(User, uid)
        for now in (late, after_midnight):
            q = daily.pick_for(db, daily.manila_today(now)).question
            _, fb = submit_response(db, user=user, question=q, answer_text="it prints something because", now=now)
            assert fb.daily_completed
        days = daily.user_days(db, user)
        assert set(days) == {date(2026, 10, 21), date(2026, 10, 22)}
        # In UTC both answers are on Oct 21; in Manila they are two days, so a 2-day streak.
        assert fb.daily_streak == 2
        assert daily.streaks(set(days), date(2026, 10, 22)) == (2, 2)
        assert daily.streaks(set(days), date(2026, 10, 24)) == (0, 2)


def test_answering_today_completes_once_and_keeps_best_score(client):
    h = auth(pid="daily-api")
    me = client.get("/api/daily/me", headers=h).json()
    assert me["completed"] is False and me["current_streak"] == 0 and len(me["last_days"]) == 14
    qid = me["question_id"]
    with SessionLocal() as db:
        ref = db.get(Question, qid).rubric["reference_answer"]
        other = db.query(Question).filter(Question.id != qid).first().id
    fb = client.post("/api/responses", headers=h, json={"question_id": other, "answer_text": "not the daily one"}).json()["feedback"]
    assert fb["daily_completed"] is False
    weak = client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "no idea at all"}).json()["feedback"]
    assert weak["daily_completed"] is True and weak["daily_streak"] == 1
    strong = client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": ref}).json()["feedback"]
    me = client.get("/api/daily/me", headers=h).json()
    assert me["completed"] and me["current_streak"] == 1 and me["best_streak"] == 1 and me["total_completed"] == 1
    assert me["score"] == max(weak["overall_score"], strong["overall_score"])
    assert me["last_days"][-1] == {"date": me["date"], "done": True, "score": me["score"]}
    with SessionLocal() as db:
        assert db.query(DailyCompletion).filter_by(question_id=qid).count() >= 1
    assert client.get("/api/daily/me").status_code == 401


# ── Safe migration ────────────────────────────────────────────────────────


def test_new_tables_are_added_without_touching_existing_data(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/live.db")
    migrate_schema(engine)
    with Session(engine) as db:
        seed_domains_and_questions(db)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE daily_completions"))
        conn.execute(text("DROP TABLE hint_usages"))
        conn.execute(text("INSERT INTO users (auth_provider, provider_account_id, display_name, created_at, last_login_at) "
                          "VALUES ('github', 'keep-me', 'Keep', '2026-01-01', '2026-01-01')"))
    assert migrate_schema(engine) is False  # same SCHEMA_VERSION: nothing is dropped
    tables = set(inspect(engine).get_table_names())
    assert {"daily_completions", "hint_usages"} <= tables
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM users WHERE provider_account_id='keep-me'")).scalar() == 1
        assert conn.execute(text("SELECT value FROM app_meta")).scalar() == SCHEMA_VERSION


# ── Progress v2 ───────────────────────────────────────────────────────────


def test_progress_v2_totals_accuracy_trend_and_recent(client):
    h = auth(pid="progress-v2")
    with SessionLocal() as db:
        today_id = daily.pick_for(db, daily.manila_today()).question.id
        qs = [q for q in db.query(Question).filter_by(language="python").all()
              if not (q.rubric or {}).get("kind") and q.id != today_id][:6]
        items = [(q.id, q.rubric["reference_answer"]) for q in qs]
    for i, (qid, ref) in enumerate(items):
        client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "no clue here" if i < 3 else ref})
    client.post(f"/api/questions/{items[0][0]}/hints", headers=h)
    client.post("/api/responses", headers=h, json={"question_id": items[0][0], "answer_text": items[0][1]})
    client.post(f"/api/questions/{items[1][0]}/skip", headers=h)
    p = client.get("/api/progress", headers=h).json()
    assert p["total_responses"] == 7 and p["total_skips"] == 1
    assert p["questions_answered"] == 6
    assert p["questions_solved"] == p["correct_answers"] == 4
    assert abs(p["accuracy"] - 4 / 7) < 1e-3
    assert p["improvement"] > 0  # wrong answers first, right ones later
    assert p["hints_used"] == 1
    assert len(p["history"]) == 30 and p["history"][-1]["answers"] == 7 and p["history"][-1]["correct"] == 4
    assert p["history"][-1]["date"] == daily.manila_today().isoformat()
    assert p["recent"][0]["question_id"] == items[0][0] and p["recent"][0]["hints_used"] == 1
    assert p["recent"][0]["verdict"] == "correct" and len(p["recent"]) == 7
    py = next(l for l in p["languages"] if l["language"] == "python")
    assert py["correct"] == 4 and py["attempts"] == 7
    assert p["current_streak"] == 0 and p["daily_done_today"] is False


def test_progress_streak_fields(client):
    uid = _user(client, "progress-streak")
    today = daily.manila_today()
    with SessionLocal() as db:
        for n in (0, 1, 2, 4, 5, 6, 7):
            q = daily.pick_for(db, today - timedelta(days=n)).question
            db.add(DailyCompletion(user_id=uid, day=(today - timedelta(days=n)).isoformat(), question_id=q.id, score=0.8))
        db.commit()
        p = get_progress(db, db.get(User, uid))
    assert (p.current_streak, p.best_streak, p.daily_done_today, p.daily_completed) == (3, 4, True, 7)
