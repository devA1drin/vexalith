"""Bookmarks: save/unsave questions and exercises, notes, filters, last results and limits."""

import pytest

from app.content.exercises import BY_SLUG as EXERCISES
from app.db.session import SessionLocal
from app.models.models import Bookmark, ExerciseAttempt, Feedback, Question, Response, User
from app.services import bookmarks
from tests.conftest import auth


def _h(pid):
    return auth(pid=pid, email=f"{pid}@example.com")


def _uid(client, pid):
    client.get("/api/me", headers=_h(pid))
    with SessionLocal() as db:
        return db.query(User).filter_by(provider_account_id=pid).one().id


def _qids(n, language=None):
    with SessionLocal() as db:
        q = db.query(Question.id).filter(Question.source == "seed")
        if language:
            q = q.filter(Question.language == language)
        return [x for (x,) in q.order_by(Question.id).limit(n).all()]


def _save(client, pid, path, **body):
    body.setdefault("saved", True)
    return client.put(f"/api/bookmarks/{path}", headers=_h(pid), json=body)


def test_bookmarks_need_sign_in(client):
    assert client.get("/api/bookmarks").status_code == 401
    assert client.get("/api/bookmarks/keys").status_code == 401
    assert client.put("/api/bookmarks/questions/1", json={"saved": True}).status_code == 401


def test_save_unsave_is_idempotent_and_private(client):
    qid = _qids(1)[0]
    assert _save(client, "bm-1", f"questions/{qid}").json() == {"key": f"q:{qid}", "saved": True, "note": ""}
    assert _save(client, "bm-1", f"questions/{qid}").json()["saved"] is True  # twice is fine
    assert client.get("/api/bookmarks/keys", headers=_h("bm-1")).json() == {"keys": [f"q:{qid}"]}
    assert client.get("/api/bookmarks/keys", headers=_h("bm-2")).json() == {"keys": []}  # someone else's
    assert _save(client, "bm-1", f"questions/{qid}", saved=False).json() == {"key": f"q:{qid}", "saved": False, "note": ""}
    assert _save(client, "bm-1", f"questions/{qid}", saved=False).status_code == 200
    assert client.get("/api/bookmarks/keys", headers=_h("bm-1")).json() == {"keys": []}


def test_unknown_items_are_refused(client):
    assert _save(client, "bm-3", "questions/999999").status_code == 404
    assert _save(client, "bm-3", "exercises/no-such-thing").status_code == 404
    assert _save(client, "bm-3", "exercises/no-such-thing", saved=False).status_code == 200  # removing is harmless


def test_notes_are_cleaned_kept_and_limited(client):
    qid = _qids(1)[0]
    out = _save(client, "bm-4", f"questions/{qid}", note="  check the\n off-by-one\u200b  ").json()
    assert out["note"] == "check the off-by-one"
    # Saving again without a note keeps it; sending a note replaces it.
    assert _save(client, "bm-4", f"questions/{qid}").json()["note"] == "check the off-by-one"
    assert _save(client, "bm-4", f"questions/{qid}", note="").json()["note"] == ""
    assert _save(client, "bm-4", f"questions/{qid}", note="x" * 141).status_code == 422


def test_list_has_cards_filters_and_counts(client):
    uid = _uid(client, "bm-5")
    py, js = _qids(2, "python"), _qids(1, "javascript")
    ex = next(iter(EXERCISES.values()))
    for qid in py + js:
        _save(client, "bm-5", f"questions/{qid}")
    _save(client, "bm-5", f"exercises/{ex['slug']}", note="loops")
    page = client.get("/api/bookmarks", headers=_h("bm-5")).json()
    assert page["counts"] == {"total": 4, "questions": 3, "exercises": 1, "shown": 4}
    assert page["items"][0]["key"] == f"x:{ex['slug']}"  # newest first
    card = page["items"][0]
    assert card["kind"] == "exercise" and card["title"] == ex["title"] and card["note"] == "loops"
    assert card["topic"].startswith("ex-") and card["result"] == "new"
    q = next(c for c in page["items"] if c["kind"] == "question")
    assert {"id", "title", "language", "topic", "topic_name", "difficulty", "question_kind", "saved_at"} <= set(q)
    langs = {o["value"]: o["count"] for o in page["filters"]["languages"]}
    assert langs["python"] >= 2 and langs["javascript"] >= 1
    assert all(c["kind"] == "question" for c in client.get("/api/bookmarks?kind=question", headers=_h("bm-5")).json()["items"])
    only_js = client.get("/api/bookmarks?language=javascript&kind=question", headers=_h("bm-5")).json()
    assert [c["id"] for c in only_js["items"]] == js and only_js["counts"]["total"] == 4
    topic = q["topic"]
    assert all(c["topic"] == topic for c in client.get(f"/api/bookmarks?topic={topic}", headers=_h("bm-5")).json()["items"])
    assert client.get("/api/bookmarks?kind=nope", headers=_h("bm-5")).status_code == 422
    assert client.get("/api/bookmarks?topic=<b>", headers=_h("bm-5")).status_code == 422
    # The profile summary counts them.
    assert client.get("/api/profile/summary", headers=_h("bm-5")).json()["bookmarks"] == 4
    assert uid


def test_cards_show_the_last_result(client):
    uid = _uid(client, "bm-6")
    a, b, c = _qids(3)
    ex = next(iter(EXERCISES.values()))
    with SessionLocal() as db:
        for qid, verdict in ((a, "wrong"), (a, "correct"), (b, "partially_correct")):
            r = Response(user_id=uid, question_id=qid, answer_text="because")
            db.add(r)
            db.flush()
            db.add(Feedback(response_id=r.id, overall_score=0.5, misconceptions=[], raw_explanation="",
                            details={"verdict": verdict}))
        db.add(ExerciseAttempt(user_id=uid, slug=ex["slug"], language=ex["language"], passed=1, total=3))
        db.commit()
    for qid in (a, b, c):
        _save(client, "bm-6", f"questions/{qid}")
    _save(client, "bm-6", f"exercises/{ex['slug']}")
    results = {i["key"]: i["result"] for i in client.get("/api/bookmarks", headers=_h("bm-6")).json()["items"]}
    assert results == {f"q:{a}": "right", f"q:{b}": "partial", f"q:{c}": "new", f"x:{ex['slug']}": "failed"}
    with SessionLocal() as db:
        db.add(ExerciseAttempt(user_id=uid, slug=ex["slug"], language=ex["language"], passed=3, total=3))
        db.commit()
    items = client.get("/api/bookmarks?kind=exercise", headers=_h("bm-6")).json()["items"]
    assert items[0]["result"] == "solved"


def test_limit_per_learner(client, monkeypatch):
    monkeypatch.setattr(bookmarks, "MAX_BOOKMARKS", 2)
    a, b, c = _qids(3)
    _save(client, "bm-7", f"questions/{a}")
    _save(client, "bm-7", f"questions/{b}")
    r = _save(client, "bm-7", f"questions/{c}")
    assert r.status_code == 409 and "up to 2" in r.json()["detail"]
    assert _save(client, "bm-7", f"questions/{a}", note="still editable").status_code == 200


def test_admin_purge_removes_bookmarks_and_settings(client, monkeypatch):
    from app.api import admin as admin_mod
    from app.models.models import UserSettings

    token = "t" * 40
    monkeypatch.setattr(admin_mod, "get_settings", lambda: type("S", (), {"admin_token": token})())
    uid = _uid(client, "bm-8")
    _save(client, "bm-8", f"questions/{_qids(1)[0]}")
    client.put("/api/profile", headers=_h("bm-8"), json={"bio": "hi"})
    ident = {"identities": ["github:bm-8"]}
    dry = client.post("/api/admin/purge-users", json=ident, headers={"X-Admin-Token": token}).json()
    assert dry["users"][0]["bookmarks"] == 1 and dry["users"][0]["settings"] == 1
    client.post("/api/admin/purge-users", json={**ident, "dry_run": False}, headers={"X-Admin-Token": token})
    with SessionLocal() as db:
        assert db.query(Bookmark).filter_by(user_id=uid).count() == 0
        assert db.get(UserSettings, uid) is None


@pytest.mark.parametrize("path", ["questions/abc", "exercises/UPPER"])
def test_bad_paths(client, path):
    assert _save(client, "bm-9", path).status_code in (404, 422)
