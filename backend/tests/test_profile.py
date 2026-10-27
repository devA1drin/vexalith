"""Profile editing: name, handle, visibility, avatar mark, bio, languages, quiz defaults, summary."""

import pytest

from app.db.session import SessionLocal
from app.models.models import LearnerProfile, User, UserSettings, XpEvent
from tests.conftest import auth


@pytest.fixture(autouse=True, scope="module")
def _off_the_leaderboard():
    yield
    with SessionLocal() as db:
        for prof in (db.query(LearnerProfile).join(User, User.id == LearnerProfile.user_id)
                     .filter(User.provider_account_id.like("pf-%"))):
            prof.visibility = "hidden"
        db.commit()


def _h(pid, **kw):
    kw.setdefault("email", f"{pid}@example.com")
    return auth(pid=pid, **kw)


def test_profile_needs_sign_in(client):
    for path in ("/api/profile", "/api/profile/summary", "/api/profile/handle?handle=abc"):
        assert client.get(path).status_code == 401
    assert client.put("/api/profile", json={"bio": "x"}).status_code == 401


def test_new_profile_has_defaults_and_never_the_email(client):
    h = _h("pf-1", name="Ada Lovelace")
    p = client.get("/api/profile", headers=h).json()
    assert p["display_name"] == "" and p["shown_name"] == "Ada Lovelace" and p["sign_in_name"] == "Ada Lovelace"
    assert p["answer_language"] == "en" and p["practice_languages"] == [] and p["bio"] == ""
    assert p["quiz_defaults"] is None and p["visibility"] == "handle" and p["handle"]
    assert p["avatar"] == "photo" and len(p["avatars"]) == 10 and "photo" not in p["avatars"]
    assert "pf-1@example.com" not in str(p) and "email" not in p


def test_name_survives_the_next_sign_in_and_can_be_cleared(client):
    h = _h("pf-2", name="Ben Cruz")
    out = client.put("/api/profile", headers=h, json={"display_name": "  Benjie   C. "}).json()
    assert out["display_name"] == "Benjie C." and out["shown_name"] == "Benjie C."
    client.get("/api/me", headers=_h("pf-2", name="Ben Cruz"))  # signing in again doesn't undo it
    assert client.get("/api/profile", headers=h).json()["shown_name"] == "Benjie C."
    assert client.get("/api/progress", headers=h).json()["display_name"] == "Benjie C."
    assert client.put("/api/profile", headers=h, json={"display_name": ""}).json()["shown_name"] == "Ben Cruz"


@pytest.mark.parametrize("bad", ["a", "x" * 41, "me@mail.com", "http://spam.example", "<b>hi</b>", "__", "Ben!"])
def test_bad_names_are_refused_with_the_field(client, bad):
    r = client.put("/api/profile", headers=_h("pf-3"), json={"display_name": bad})
    assert r.status_code == 422 and r.json()["field"] == "display_name"


def test_filipino_names_with_accents_are_fine(client):
    out = client.put("/api/profile", headers=_h("pf-4"), json={"display_name": "Maria Niña O'Brien-Santos"}).json()
    assert out["display_name"] == "Maria Niña O'Brien-Santos"


def test_invisible_characters_are_stripped(client):
    out = client.put("/api/profile", headers=_h("pf-4"), json={"display_name": "Ni\u200bna"}).json()
    assert out["display_name"] == "Nina"


def test_handles_are_unique_ignoring_case(client):
    a, b = _h("pf-5"), _h("pf-6")
    assert client.put("/api/profile", headers=a, json={"handle": "Loop Wizard"}).json()["handle"] == "Loop Wizard"
    r = client.put("/api/profile", headers=b, json={"handle": "loop wizard"})
    assert r.status_code == 422 and r.json() == {"detail": "Someone already has that handle.", "field": "handle"}
    check = client.get("/api/profile/handle", headers=b, params={"handle": "LOOP WIZARD"}).json()
    assert check["available"] is False
    # Your own handle is "available" to you, and a free one is too.
    assert client.get("/api/profile/handle", headers=a, params={"handle": "loop wizard"}).json()["available"] is True
    assert client.get("/api/profile/handle", headers=b, params={"handle": "Byte Owl 7"}).json() == {
        "handle": "Byte Owl 7", "available": True, "reason": ""}


@pytest.mark.parametrize("bad", ["ab", "x" * 25, "admin", "Anonymous Fox", "-dash", "emoji🙂", "pf-7"])
def test_bad_handles_are_refused(client, bad):
    r = client.put("/api/profile", headers=_h("pf-7"), json={"handle": bad})
    assert r.status_code == 422 and r.json()["field"] == "handle"
    assert client.get("/api/profile/handle", headers=_h("pf-7"), params={"handle": bad}).json()["available"] is False


def test_a_bad_field_saves_nothing(client):
    h = _h("pf-8")
    r = client.put("/api/profile", headers=h, json={"display_name": "Cara Diaz", "bio": "<script>"})
    assert r.status_code == 422 and r.json()["field"] == "bio"
    assert client.get("/api/profile", headers=h).json()["display_name"] == ""


def test_visibility_is_the_same_setting_as_the_leaderboard(client):
    h = _h("pf-9", name="Dina Reyes")
    client.put("/api/profile", headers=h, json={"display_name": "Dee R", "visibility": "name"})
    assert client.get("/api/xp/profile", headers=h).json()["visibility"] == "name"
    assert client.get("/api/xp/profile", headers=h).json()["shown_as"] == "Dee R"
    client.put("/api/xp/profile", headers=h, json={"visibility": "hidden"})
    p = client.get("/api/profile", headers=h).json()
    assert p["visibility"] == "hidden" and p["leaderboard_name"] is None
    assert client.put("/api/profile", headers=h, json={"visibility": "everyone"}).status_code == 422


def test_avatar_marks_and_the_leaderboard(client):
    h = _h("pf-10", picture=None)
    p = client.get("/api/profile", headers=h).json()
    assert p["avatar"] == "initials-ink" and p["photo_url"] is None
    assert client.put("/api/profile", headers=h, json={"avatar": "photo"}).status_code == 422  # no photo to use
    assert client.put("/api/profile", headers=h, json={"avatar": "https://x.example/a.png"}).status_code == 422
    assert client.put("/api/profile", headers=h, json={"avatar": "mark-circuit"}).json()["avatar"] == "mark-circuit"
    with SessionLocal() as db:
        uid = db.query(User).filter_by(provider_account_id="pf-10").one().id
        db.add(XpEvent(user_id=uid, key="test:pf-10", kind="answer", amount=5))
        db.commit()
    board = client.get("/api/leaderboard", headers=h).json()
    assert board["you"]["avatar"] == "mark-circuit"
    assert [e["avatar"] for e in board["entries"] if e["is_you"]] == ["mark-circuit"]
    assert not any(str(e["avatar"] or "").startswith("http") for e in board["entries"])  # never a photo URL
    client.put("/api/profile", headers=h, json={"visibility": "anonymous"})
    assert client.get("/api/leaderboard", headers=h).json()["you"]["avatar"] is None  # anonymous shows no mark


def test_bio_limits(client):
    h = _h("pf-11")
    out = client.put("/api/profile", headers=h, json={"bio": "  Learning Python\n\n\nand Java  "}).json()
    assert out["bio"] == "Learning Python\nand Java"
    assert client.put("/api/profile", headers=h, json={"bio": "x" * 161}).json()["field"] == "bio"
    assert client.put("/api/profile", headers=h, json={"bio": "a\nb\nc\nd"}).json()["field"] == "bio"
    assert client.put("/api/profile", headers=h, json={"bio": ""}).json()["bio"] == ""


def test_languages_and_answer_language(client):
    h = _h("pf-12")
    out = client.put("/api/profile", headers=h, json={"practice_languages": ["java", "python", "java"],
                                                      "answer_language": "taglish"}).json()
    assert out["practice_languages"] == ["java", "python"] and out["answer_language"] == "taglish"
    assert client.put("/api/profile", headers=h, json={"practice_languages": ["cobol"]}).status_code == 422
    assert client.put("/api/profile", headers=h, json={"answer_language": "es"}).status_code == 422


def test_quiz_defaults_are_checked_and_offered_to_the_quiz_page(client):
    h = _h("pf-13")
    opts = client.get("/api/quiz/options", headers=h).json()
    assert opts["defaults"] is None
    lang = opts["scopes"]["language"][0]["value"]
    pick = {"scope": "language", "value": lang, "length": opts["lengths"][0], "minutes": opts["minutes"][-1], "instant": True}
    assert client.put("/api/profile", headers=h, json={"quiz_defaults": pick}).json()["quiz_defaults"] == pick
    assert client.get("/api/quiz/options", headers=h).json()["defaults"] == pick
    bad = {**pick, "value": "nope"}
    assert client.put("/api/profile", headers=h, json={"quiz_defaults": bad}).json()["field"] == "quiz_defaults"
    assert client.put("/api/profile", headers=h, json={"quiz_defaults": {**pick, "length": 7}}).status_code == 422
    assert client.put("/api/profile", headers=h, json={"quiz_defaults": None}).json()["quiz_defaults"] is None
    assert client.get("/api/quiz/options", headers=h).json()["defaults"] is None


def test_a_stale_saved_default_is_ignored(client):
    h = _h("pf-14")
    client.get("/api/profile", headers=h)
    with SessionLocal() as db:
        uid = db.query(User).filter_by(provider_account_id="pf-14").one().id
        db.get(UserSettings, uid).quiz_defaults = {"scope": "topic", "value": "gone", "length": 10, "minutes": 10}
        db.commit()
    assert client.get("/api/quiz/options", headers=h).json()["defaults"] is None


def test_summary_is_read_only_numbers(client):
    h = _h("pf-15")
    s = client.get("/api/profile/summary", headers=h).json()
    for k in ("level", "xp", "badges_earned", "badges_total", "paths", "paths_finished", "bookmarks", "joined_at"):
        assert k in s
    assert s["badges_total"] >= 20 and 0 <= s["badges_earned"] <= s["badges_total"] and s["bookmarks"] == 0 and s["paths"]
    assert {"slug", "name", "steps_done", "steps_total", "progress"} <= set(s["paths"][0])


def test_public_feedback_uses_the_chosen_name_and_mark(client):
    h = _h("pf-16", name="Eli Santos")
    client.put("/api/profile", headers=h, json={"display_name": "Eli S", "avatar": "mark-dots"})
    r = client.post("/api/feedback", headers=h, json={"rating": 5, "category": "other", "message": "Clear and useful hints."})
    assert r.status_code in (200, 201), r.text
    wall = client.get("/api/feedback/recent").json()
    mine = [f for f in wall if f["author_name"] == "Eli S"]
    assert mine and mine[0]["author_avatar"] == "mark-dots" and mine[0]["author_avatar_url"] is None
