"""Fundamentals onboarding, level ladder and focus mode."""

from tests.conftest import auth
from tests.test_languages import graduate

LANGS = ["python", "javascript", "php", "html", "css", "general"]


def test_new_user_starts_with_fundamentals_level_one_in_every_language(client):
    for lang in LANGS:
        q = client.get(f"/api/questions/next?language={lang}", headers=auth(pid=f"fund-new-{lang}")).json()
        assert q["domain_slug"] == "fundamentals", lang
        assert q["difficulty"] == "beginner", lang
        assert q["language"] in {lang, "general"}


def test_onboarding_skips_stay_in_fundamentals_and_rotate(client):
    h = auth(pid="fund-skip")
    q = client.get("/api/questions/next?language=python", headers=h).json()
    seen = [q["id"]]
    for _ in range(8):
        q = client.post(f"/api/questions/{q['id']}/skip?language=python", headers=h).json()["next_question"]
        assert q["domain_slug"] == "fundamentals"
        assert q["id"] not in seen
        seen.append(q["id"])


def test_onboarding_ends_after_clearing_fundamentals(client):
    h = auth(pid="fund-grad")
    graduate(client, h, "javascript")
    prog = client.get("/api/progress", headers=h).json()
    assert prog["domains"][0]["domain_slug"] == "fundamentals"
    f = prog["fundamentals"]
    assert f["answers"] == 5 and f["cleared"] is True and f["recent_average"] >= f["pass_average"]
    # Broadens: other skills now appear.
    q = client.get("/api/questions/next?language=javascript", headers=h).json()
    domains = {q["domain_slug"]}
    for _ in range(10):
        q = client.post(f"/api/questions/{q['id']}/skip?language=javascript", headers=h).json()["next_question"]
        domains.add(q["domain_slug"])
    assert domains - {"fundamentals"}


def test_level_ladder_moves_up_after_strong_answers(client):
    h = auth(pid="fund-ladder")
    graduate(client, h, "php", n=3)  # 3 strong answers → level 2
    q = client.get("/api/questions/next?language=php", headers=h).json()
    assert q["domain_slug"] == "fundamentals" and q["difficulty"] == "intermediate"


def test_weak_answers_keep_learner_in_fundamentals(client):
    h = auth(pid="fund-weak")
    for _ in range(6):
        q = client.get("/api/questions/next?language=python", headers=h).json()
        assert q["domain_slug"] == "fundamentals" and q["difficulty"] == "beginner"
        client.post("/api/responses", headers=h, json={"question_id": q["id"], "answer_text": "I am not sure what this does yet."})
    prog = client.get("/api/progress", headers=h).json()
    assert prog["fundamentals"]["cleared"] is False


def test_focus_mode_keeps_fundamentals_after_graduation(client):
    h = auth(pid="fund-focus")
    graduate(client, h, "css")
    q = client.get("/api/questions/next?language=css&focus=fundamentals", headers=h).json()
    assert q["domain_slug"] == "fundamentals"
    for _ in range(10):
        q = client.post(f"/api/questions/{q['id']}/skip?language=css&focus=fundamentals", headers=h).json()["next_question"]
        assert q["domain_slug"] == "fundamentals" and q["language"] in {"css", "general"}


def test_unknown_focus_rejected(client):
    r = client.get("/api/questions/next?language=python&focus=debugging", headers=auth(pid="fund-x"))
    assert r.status_code == 422


def test_onboarding_mostly_uses_the_chosen_language(client):
    langs = []
    for i in range(12):
        q = client.get("/api/questions/next?language=php", headers=auth(pid=f"fund-mix-{i}")).json()
        langs.append(q["language"])
    assert langs.count("php") >= 4  # ~75% expected; loose bound keeps it deterministic in practice
