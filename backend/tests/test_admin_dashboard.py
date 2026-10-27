"""Admin dashboard: access rules, learner actions, question edits, feedback moderation, audit."""

import re

import pytest

from tests.conftest import auth

ADMIN = dict(pid="adm-1", name="Admin Person", email="admin@example.com")
OTHER = dict(pid="not-admin-1", name="Plain Learner", email="plain@example.com")


@pytest.fixture
def admins(monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "admin_identities", "github:adm-1, google:someone-else")
    return auth(**ADMIN)


def _admin_routes():
    from app.main import app

    out = []
    for path, ops in app.openapi()["paths"].items():
        if path.startswith("/api/admin") and "purge-users" not in path:
            for m in ops:
                out.append((m.upper(), re.sub(r"\{[^}]+\}", "1", path)))
    return out


def test_every_admin_route_needs_sign_in_then_admin(client, admins):
    routes = _admin_routes()
    assert len(routes) >= 15
    for method, path in routes:
        assert client.request(method, path, json={}).status_code == 401, (method, path)
        assert client.request(method, path, json={}, headers=auth(**OTHER)).status_code == 403, (method, path)
        assert client.request(method, path, json={}, headers={"Authorization": "Bearer junk"}).status_code == 401
    for path in ("/api/admin/me", "/api/admin/overview", "/api/admin/learners", "/api/admin/questions",
                 "/api/admin/exercises", "/api/admin/feedback", "/api/admin/audit"):
        assert client.get(path, headers=admins).status_code == 200, path


def test_nobody_is_admin_when_unset(client):
    # Same identity as the admin above, but ADMIN_IDENTITIES is empty here.
    assert client.get("/api/admin/me", headers=auth(**ADMIN)).status_code == 403


def test_admin_is_by_identity_not_email(client, admins):
    # Same email as the admin, different account: not an admin.
    impostor = auth(pid="adm-2", name="Impostor", email="admin@example.com")
    assert client.get("/api/admin/me", headers=impostor).status_code == 403
    assert client.get("/api/admin/me", headers=auth(provider="google", pid="adm-1")).status_code == 403
    assert client.get("/api/admin/me", headers=admins).json()["identity"] == "github:adm-1"


def test_profile_says_who_is_admin(client, admins):
    assert client.get("/api/profile", headers=admins).json()["is_admin"] is True
    assert client.get("/api/profile", headers=auth(**OTHER)).json()["is_admin"] is False


def _answer(client, h, language="python", text="It returns early because the loop never runs on empty input."):
    q = client.get(f"/api/questions/next?language={language}", headers=h).json()
    r = client.post("/api/responses", json={"question_id": q["id"], "answer_text": text}, headers=h)
    assert r.status_code in (200, 201), r.text
    return q["id"]


def test_overview_and_learner_list(client, admins):
    h = auth(pid="ov-1", name="Overview Learner", email="overview.learner@example.com")
    _answer(client, h)
    client.get("/api/xp", headers=h)
    ov = client.get("/api/admin/overview", headers=admins).json()
    t = ov["totals"]
    assert t["learners"] >= 1 and t["attempts"] >= 1 and t["active_7d"] >= 1 and t["active_30d"] >= t["active_7d"]
    assert len(ov["daily"]) == 30 and sum(d["answers"] for d in ov["daily"]) >= 1
    assert ov["by_topic"] and ov["by_language"]
    found = client.get("/api/admin/learners?q=overview.learner@", headers=admins).json()
    assert found["total"] == 1
    row = found["items"][0]
    assert row["email"] == "overview.learner@example.com" and row["attempts"] >= 1 and row["last_active"]
    assert row["identity"] == "github:ov-1"
    page = client.get("/api/admin/learners?sort=xp&page=1", headers=admins).json()
    assert page["pages"] >= 1 and len(page["items"]) <= 20


def test_emails_stay_out_of_other_admin_payloads(client, admins):
    h = auth(pid="mail-1", name="Mail Person", email="secret.mail@example.com")
    _answer(client, h)
    client.post("/api/feedback", json={"rating": 5, "category": "other", "message": "lovely app for mail test"}, headers=h)
    for path in ("/api/admin/overview", "/api/admin/feedback", "/api/admin/audit", "/api/admin/questions"):
        assert "secret.mail@example.com" not in client.get(path, headers=admins).text, path


def _uid(client, admins, q):
    return client.get(f"/api/admin/learners?q={q}", headers=admins).json()["items"][0]


def test_hide_from_leaderboard(client, admins):
    h = auth(pid="board-1", name="Board Person")
    _answer(client, h, text="The loop stops when i reaches n, so the last index is never read and it prints 3.")
    me = client.get("/api/xp", headers=h).json()
    row = _uid(client, admins, "github:board-1")
    r = client.post(f"/api/admin/learners/{row['id']}/board", json={"hidden": True}, headers=admins)
    assert r.status_code == 200 and r.json()["board_hidden"] is True
    board = client.get("/api/leaderboard?period=all", headers=h).json()
    assert all(not e["is_you"] for e in board["entries"])
    assert board["you"]["rank"] is None
    client.post(f"/api/admin/learners/{row['id']}/board", json={"hidden": False}, headers=admins)
    if me.get("total_xp", me.get("xp", 0)):
        assert client.get("/api/leaderboard?period=all", headers=h).json()["you"]["rank"] is not None
    actions = [a["action"] for a in client.get("/api/admin/audit", headers=admins).json()["items"]]
    assert "learner.board_hidden" in actions and "learner.board_shown" in actions


def test_reset_xp_needs_confirmation_and_is_audited(client, admins):
    from app.db.session import SessionLocal
    from app.models.models import XpEvent

    h = auth(pid="xp-1", name="Xp Person")
    _answer(client, h)
    client.get("/api/xp", headers=h)
    row = _uid(client, admins, "github:xp-1")
    with SessionLocal() as db:
        db.add(XpEvent(user_id=row["id"], key="test:bonus", kind="answer", amount=40, label="test"))
        db.commit()
    assert client.post(f"/api/admin/learners/{row['id']}/reset-xp", json={"confirm": "nope"}, headers=admins).status_code == 400
    r = client.post(f"/api/admin/learners/{row['id']}/reset-xp", json={"confirm": row["confirm_word"]}, headers=admins)
    assert r.status_code == 200 and r.json()["xp"] == 0
    client.get("/api/xp", headers=h)  # syncing doesn't hand the old awards back
    assert _uid(client, admins, "github:xp-1")["xp"] == 0
    entry = next(a for a in client.get("/api/admin/audit", headers=admins).json()["items"] if a["action"] == "learner.xp_reset")
    assert entry["details"]["previous_xp"] >= 40 and "@" in entry["target"]


def test_admin_cannot_delete_or_reset_self(client, admins):
    client.get("/api/profile", headers=admins)
    me = _uid(client, admins, "github:adm-1")
    for action in ("delete", "reset-xp"):
        r = client.post(f"/api/admin/learners/{me['id']}/{action}", json={"confirm": me["confirm_word"]}, headers=admins)
        assert r.status_code == 400


def test_delete_learner_removes_every_row(client, admins):
    from sqlalchemy import inspect

    from app.db.base import Base
    from app.db.session import SessionLocal, engine
    from app.models.models import FeedbackModeration, UserFeedback

    h = auth(pid="gone-1", name="Gone Person", email="gone@example.com")
    qid = _answer(client, h)
    client.post(f"/api/questions/{qid}/skip?language=python", headers=h)
    client.post("/api/feedback", json={"rating": 3, "category": "other", "message": "delete me please now"}, headers=h)
    client.get("/api/xp", headers=h)
    client.put("/api/profile", json={"display_name": "Gone", "bio": "bye"}, headers=h)
    client.post("/api/bookmarks", json={"item": f"question:{qid}"}, headers=h)
    client.get("/api/paths/python/steps/1/next", headers=h)
    row = _uid(client, admins, "github:gone-1")
    client.post(f"/api/admin/learners/{row['id']}/board", json={"hidden": True}, headers=admins)
    fid = client.get("/api/admin/feedback?q=delete me please", headers=admins).json()["items"][0]["id"]
    client.post(f"/api/admin/feedback/{fid}/review", json={"reviewed": True}, headers=admins)

    assert client.post(f"/api/admin/learners/{row['id']}/delete", json={"confirm": "wrong"}, headers=admins).status_code == 400
    r = client.post(f"/api/admin/learners/{row['id']}/delete", json={"confirm": "@" + row["confirm_word"]}, headers=admins)
    assert r.status_code == 200
    removed = r.json()["removed"]
    assert removed["responses"] >= 1 and removed["flags"] == 1 and removed["profile"] == 1 and removed["feedback_reviews"] == 1

    # Walk every table: nothing with this user's id is left behind.
    with SessionLocal() as db:
        for table in Base.metadata.sorted_tables:
            cols = [c.name for c in table.columns]
            fk_user = [c.name for c in table.columns if any(fk.column.table.name == "users" for fk in c.foreign_keys)]
            for col in fk_user:
                left = db.execute(table.select().where(table.c[col] == row["id"])).fetchall()
                assert not left, (table.name, col)
            assert "users" in inspect(engine).get_table_names() and cols
        assert db.query(UserFeedback).filter_by(id=fid).count() == 0
        assert db.query(FeedbackModeration).filter_by(feedback_id=fid).count() == 0
    assert client.get("/api/admin/learners?q=github:gone-1", headers=admins).json()["total"] == 0
    entry = next(a for a in client.get("/api/admin/audit", headers=admins).json()["items"] if a["action"] == "learner.deleted")
    assert "gone@example.com" not in str(entry)


def test_purge_covers_every_user_table():
    """Every table that points at users must be in the shared purge list."""
    from app.db.base import Base
    from app.services.purge import OWNED

    covered = {model.__tablename__ for _n, model, _c in OWNED} | {"users"}
    for table in Base.metadata.sorted_tables:
        if any(fk.column.table.name == "users" for c in table.columns for fk in c.foreign_keys):
            assert table.name in covered, table.name


def test_question_edit_survives_reseed_and_checks_style(client, admins):
    from app.db.session import SessionLocal
    from app.services.question_bank import seed_domains_and_questions

    lst = client.get("/api/admin/questions?language=python&kind=explain", headers=admins).json()
    qid = lst["items"][0]["id"]
    before = client.get(f"/api/admin/questions/{qid}", headers=admins).json()
    assert before["task_line"] and before["question_text"] and before["key_idea"]

    check = client.post(f"/api/admin/questions/{qid}", headers=admins, json={
        "question_text": "What does this print? Explain your answer in your own words",
        "key_idea": "Line 1 sets x. Line 2 adds one.", "check_only": True}).json()
    assert check["saved"] is False and len(check["notes"]) >= 3
    assert client.get(f"/api/admin/questions/{qid}", headers=admins).json()["question_text"] == before["question_text"]

    new_text = "What does this function return when the list is empty?"
    new_idea = ("A loop over an empty list never runs, so whatever the accumulator started as is the answer. "
                "Check the starting value first; forgetting the empty case is the usual slip.")
    r = client.post(f"/api/admin/questions/{qid}", headers=admins, json={"question_text": new_text, "key_idea": new_idea}).json()
    assert r["saved"] and r["notes"] == []
    assert r["question"]["question_text"] == new_text and r["question"]["task_line"] == before["task_line"]
    assert r["question"]["edited"] is True

    with SessionLocal() as db:
        seed_domains_and_questions(db)  # what every startup does
    after = client.get(f"/api/admin/questions/{qid}", headers=admins).json()
    assert after["question_text"] == new_text and after["key_idea"] == new_idea
    learner = client.get(f"/api/questions/{qid}", headers=auth(**OTHER))
    if learner.status_code == 200:
        assert learner.json()["prompt"].startswith(new_text)
    entry = next(a for a in client.get("/api/admin/audit", headers=admins).json()["items"] if a["action"] == "question.edited")
    assert set(entry["details"]["fields"]) == {"question_text", "key_idea"}
    assert client.post(f"/api/admin/questions/{qid}", headers=admins, json={"question_text": "  "}).status_code == 422


def test_hidden_questions_are_not_served(client, admins):
    from app.db.session import SessionLocal
    from app.services import paths, quiz

    qid = client.get("/api/admin/questions?language=css", headers=admins).json()["items"][0]["id"]
    with SessionLocal() as db:
        n_before = len(quiz._pool(db, "language", "css"))
    assert client.post(f"/api/admin/questions/{qid}/visibility", json={"hidden": True}, headers=admins).json()["hidden"] is True
    with SessionLocal() as db:
        assert qid not in {q.id for q, _d in quiz._pool(db, "language", "css")}
        assert len(quiz._pool(db, "language", "css")) == n_before - 1
        assert qid not in {c[0] for c in paths._catalog(db)}
    h = auth(pid="hid-1", name="Hidden Tester")
    for _ in range(12):
        q = client.get("/api/questions/next?language=css", headers=h).json()
        assert q["id"] != qid
        client.post(f"/api/questions/{q['id']}/skip?language=css", headers=h)
    assert client.get("/api/admin/questions?status=hidden", headers=admins).json()["total"] >= 1
    client.post(f"/api/admin/questions/{qid}/visibility", json={"hidden": False}, headers=admins)
    with SessionLocal() as db:
        assert len(quiz._pool(db, "language", "css")) == n_before


def test_new_question_follows_house_shape(client, admins):
    body = {
        "topic": "logic_problems", "language": "general", "difficulty": "beginner",
        "title": "Admin test: two doors", "code": "",
        "question_text": "One guard always lies and one always tells the truth. What single question finds the safe door?",
        "key_points": "Ask what the other guard would say — other guard, would say\nPick the opposite door — opposite",
        "reference_answer": "Ask either guard which door the other would call safe, then take the other door.",
        "key_idea": "Route the question through both guards so the lie is applied exactly once; then the answer is always wrong and you flip it.",
    }
    r = client.post("/api/admin/questions", json=body, headers=admins)
    assert r.status_code == 200, r.text
    q = r.json()["question"]
    assert q["source"] == "admin" and q["task_line"] and q["key_idea"] == body["key_idea"]
    assert len(q["hints"]) == 3 and q["key_points"] == ["Ask what the other guard would say", "Pick the opposite door"]
    assert client.post("/api/admin/questions", json=body, headers=admins).status_code == 409
    assert client.get("/api/admin/questions?status=new", headers=admins).json()["total"] >= 1
    assert client.post("/api/admin/questions", json={**body, "topic": "nope", "title": "x y z"}, headers=admins).status_code == 422
    from app.db.session import SessionLocal
    from app.models.models import Question

    with SessionLocal() as db:  # keep the shared test bank equal to the seed bank
        db.query(Question).filter_by(id=q["id"]).delete()
        db.commit()


def test_feedback_moderation(client, admins):
    h = auth(pid="fb-1", name="Feedback Person")
    client.post("/api/feedback", json={"rating": 2, "category": "bug", "message": "the moderation test message"}, headers=h)
    items = client.get("/api/admin/feedback?status=new&q=moderation test", headers=admins).json()["items"]
    fid = items[0]["id"]
    assert items[0]["reviewed_at"] is None and items[0]["author"]["name"]
    client.post(f"/api/admin/feedback/{fid}/review", json={"reviewed": True}, headers=admins)
    assert client.get("/api/admin/feedback?status=reviewed&q=moderation test", headers=admins).json()["total"] == 1
    assert any(f["id"] == fid for f in client.get("/api/feedback/recent").json())
    client.post(f"/api/admin/feedback/{fid}/visibility", json={"hidden": True}, headers=admins)
    assert all(f["id"] != fid for f in client.get("/api/feedback/recent").json())
    assert client.get("/api/admin/feedback?status=hidden&q=moderation test", headers=admins).json()["total"] == 1
    assert client.get("/api/admin/feedback?category=bug&rating=2&q=moderation test", headers=admins).json()["total"] == 1
    assert client.post(f"/api/admin/feedback/{fid}/delete", headers=admins).json()["deleted"]
    assert client.get("/api/admin/feedback?q=moderation test", headers=admins).json()["total"] == 0
    assert client.post(f"/api/admin/feedback/{fid}/delete", headers=admins).status_code == 404
    acts = {a["action"] for a in client.get("/api/admin/audit", headers=admins).json()["items"]}
    assert {"feedback.reviewed", "feedback.hidden", "feedback.deleted"} <= acts
    only = client.get("/api/admin/audit?action=feedback.deleted", headers=admins).json()
    assert only["items"] and all(a["action"] == "feedback.deleted" for a in only["items"])


def test_rating_rises_when_learners_miss():
    from datetime import datetime, timedelta, timezone

    from app.db.session import SessionLocal
    from app.services.admin import question_stats

    with SessionLocal() as db:
        from app.models.models import Question

        q = db.query(Question).first()
        start = question_stats(db, answers=[])[q.id]["rating"]
        t = datetime.now(timezone.utc)
        misses = [(i, 9000 + i, q.id, t + timedelta(seconds=i), "incorrect", 0.1) for i in range(6)]
        hits = [(i, 9000 + i, q.id, t + timedelta(seconds=i), "correct", 1.0) for i in range(6)]
        hard = question_stats(db, answers=misses)[q.id]
        easy = question_stats(db, answers=hits)[q.id]
        assert hard["rating"] > start > easy["rating"]
        assert hard["fail_rate"] == 1.0 and easy["pass_rate"] == 1.0 and hard["learners"] == 6


def test_exercises_stats(client, admins):
    items = client.get("/api/admin/exercises", headers=admins).json()["items"]
    assert len(items) >= 50 and {"slug", "runs", "solve_rate", "topic"} <= set(items[0])


def test_style_notes_flag_walkthroughs_but_not_output_lines():
    from app.services.question_edits import style_notes
    walk = style_notes(question_text="What does this print?", key_idea="On line 2 the loop starts, then line 3 adds one to the total each pass, so the sum grows.", reference_answer="")
    assert any("line-by-line" in n for n in walk)
    output = style_notes(question_text="What does this print?", key_idea="Strings are immutable, so a method returns a new value and the old name still points at the original text.",
                         reference_answer="The first line is ADA, the second line is 15 because the name never changed.")
    assert not any("line-by-line" in n for n in output)


def test_rate_sorts_rank_well_answered_questions_first(client, admins):
    r = client.get("/api/admin/questions?sort=fail_rate", headers=admins)
    assert r.status_code == 200
    items = [i for i in r.json()["items"] if i["attempts"]]
    thin_seen = False
    for i in items:
        if i["attempts"] < 3:
            thin_seen = True
        else:
            assert not thin_seen, "a question with 3+ answers came after one with fewer"
