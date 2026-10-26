from tests.conftest import auth

TOKEN = "t" * 40


def test_admin_disabled_without_token(client):
    r = client.post("/api/admin/purge-users", json={"identities": ["github:x"]}, headers={"X-Admin-Token": "anything"})
    assert r.status_code == 404


def test_admin_purge(client, monkeypatch):
    from app.api import admin as admin_mod
    monkeypatch.setattr(admin_mod, "get_settings", lambda: type("S", (), {"admin_token": TOKEN})())

    h = auth(pid="purge-me", name="Purge Me")
    q = client.get("/api/questions/next?language=python", headers=h).json()
    client.post(f"/api/questions/{q['id']}/skip?language=python", headers=h)
    client.post("/api/responses", json={"question_id": q["id"], "answer_text": "Because the loop exits early on empty input."}, headers=h)
    assert client.post("/api/feedback", json={"rating": 4, "category": "other", "message": "purge test entry"}, headers=h).status_code == 201
    assert client.get("/api/xp", headers=h).status_code == 200  # creates the leaderboard profile
    assert client.get("/api/paths/python/steps/1/next", headers=h).status_code == 200  # remembers the step
    assert client.post("/api/paths/python/steps/3/skip-ahead", headers=h).status_code == 200

    assert client.post("/api/admin/purge-users", json={"identities": ["github:purge-me"]}, headers={"X-Admin-Token": "wrong"}).status_code == 403
    dry = client.post("/api/admin/purge-users", json={"identities": ["github:purge-me"]}, headers={"X-Admin-Token": TOKEN}).json()
    assert dry["dry_run"] and dry["users"][0]["responses"] == 1 and dry["users"][0]["feedback_entries"] == 1
    assert dry["users"][0]["path_activity"] == 1 and dry["users"][0]["path_skips"] == 1
    real = client.post("/api/admin/purge-users", json={"identities": ["github:purge-me", "github:nobody"], "dry_run": False}, headers={"X-Admin-Token": TOKEN}).json()
    assert real["users"][0]["found"] and real["users"][1]["found"] is False
    wall = client.get("/api/feedback/recent").json()
    assert all(f["message"] != "purge test entry" for f in wall)
    from app.db.session import SessionLocal
    from app.models.models import LearnerProfile, PathActivity, PathSkip, User, UserBadge, XpEvent
    with SessionLocal() as db:
        assert db.query(User).filter_by(provider_account_id="purge-me").count() == 0
        live = {u for (u,) in db.query(User.id).all()}
        for model in (LearnerProfile, XpEvent, UserBadge, PathActivity, PathSkip):
            assert {u for (u,) in db.query(model.user_id).all()} <= live  # nothing left behind
    again = client.post("/api/admin/purge-users", json={"identities": ["github:purge-me"]}, headers={"X-Admin-Token": TOKEN}).json()
    assert again["users"][0]["found"] is False
