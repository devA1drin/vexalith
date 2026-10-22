"""API tests: auth, adaptive flow, skip/next, progress, product feedback."""

from tests.conftest import auth, mint


def test_health_public(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["auth_configured"] is True
    assert body["question_count"] >= 72


def test_requires_valid_jwt(client):
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/me", headers={"Authorization": "Bearer nope"}).status_code == 401
    bad_sig = mint(secret="some-other-secret-0123456789abcdef")
    assert client.get("/api/me", headers={"Authorization": f"Bearer {bad_sig}"}).status_code == 401
    expired = mint(lifetime=-120)
    assert client.get("/api/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    too_long = mint(lifetime=24 * 3600)
    assert client.get("/api/me", headers={"Authorization": f"Bearer {too_long}"}).status_code == 401
    wrong_aud = mint(aud="someone-else")
    assert client.get("/api/me", headers={"Authorization": f"Bearer {wrong_aud}"}).status_code == 401
    spoofed_sub = mint(sub="github:999")
    assert client.get("/api/me", headers={"Authorization": f"Bearer {spoofed_sub}"}).status_code == 401
    assert client.get("/api/questions/next").status_code == 401
    assert client.post("/api/responses", json={"question_id": 1, "answer_text": "x" * 20}).status_code == 401
    assert client.get("/api/progress").status_code == 401


def test_me_upserts_user_by_provider_identity(client):
    h = auth(pid="2001", name="Grace")
    a = client.get("/api/me", headers=h).json()
    b = client.get("/api/me", headers=auth(pid="2001", name="Grace Hopper")).json()
    assert a["id"] == b["id"] and b["display_name"] == "Grace Hopper"
    other = client.get("/api/me", headers=auth(provider="google", pid="2001")).json()
    assert other["id"] != a["id"]


def test_practice_flow_language_skip_and_next(client):
    h = auth(pid="3001")
    q1 = client.get("/api/questions/next?language=javascript", headers=h).json()
    assert q1["language"] in {"javascript", "general"} and q1["code"]
    r = client.get("/api/questions/next?language=javascript", headers=h)
    assert r.headers.get("cache-control") == "no-store"

    # Skip → different question, recorded, small mastery nudge only.
    s = client.post(f"/api/questions/{q1['id']}/skip?language=javascript", headers=h)
    assert s.status_code == 200
    q2 = s.json()["next_question"]
    assert q2["id"] != q1["id"]

    # Answer q2 → Next gives a question different from both.
    resp = client.post("/api/responses", headers=h,
                       json={"question_id": q2["id"], "answer_text": "Because the loop runs n times, it is O(n)."})
    assert resp.status_code == 201
    fb = resp.json()["feedback"]
    assert fb["verdict"] in {"correct", "partially_correct", "incorrect"}
    assert fb["provider_used"] == "heuristic"
    q3 = client.get("/api/questions/next?language=javascript", headers=h).json()
    assert q3["id"] not in {q1["id"], q2["id"]}

    # Several skips in a row never repeat recent questions.
    seen = {q1["id"], q2["id"], q3["id"]}
    cur = q3
    for _ in range(5):
        nxt = client.post(f"/api/questions/{cur['id']}/skip?language=javascript", headers=h).json()["next_question"]
        assert nxt["id"] not in seen
        seen.add(nxt["id"])
        cur = nxt

    prog = client.get("/api/progress", headers=h).json()
    assert prog["total_responses"] == 1
    assert prog["total_skips"] == 6
    from app.content.domains import DOMAINS
    assert len(prog["domains"]) == len(DOMAINS)
    assert prog["languages"] and prog["languages"][0]["attempts"] == 1
    # skips alone don't tank mastery (the answered skill may drop from a weak answer)
    assert all(d["mastery"] >= 0.4 for d in prog["domains"] if d["domain_slug"] != q2["domain_slug"])


def test_python_default_language(client):
    q = client.get("/api/questions/next", headers=auth(pid="3002")).json()
    assert q["language"] in {"python", "general"}


def test_product_feedback_validation_rate_limit_and_privacy(client):
    h = auth(pid="4001", name="Linus", email="linus@example.com")
    bad = client.post("/api/feedback", headers=h, json={"rating": 6, "category": "bug", "message": "hello there"})
    assert bad.status_code == 422
    bad = client.post("/api/feedback", headers=h, json={"rating": 3, "category": "spam", "message": "hello there"})
    assert bad.status_code == 422
    bad = client.post("/api/feedback", headers=h, json={"rating": 3, "category": "bug", "message": "   "})
    assert bad.status_code == 422
    links = "see http://a.com http://b.com http://c.com"
    assert client.post("/api/feedback", headers=h, json={"rating": 3, "category": "bug", "message": links}).status_code == 422
    assert client.post("/api/feedback", json={"rating": 3, "category": "bug", "message": "no auth here"}).status_code == 401

    ok = client.post("/api/feedback", headers=h,
                     json={"rating": 5, "category": "feature_request", "message": "Add Rust questions!", "page_context": "/practice"})
    assert ok.status_code == 201
    dup = client.post("/api/feedback", headers=h,
                      json={"rating": 5, "category": "feature_request", "message": "add rust   questions!"})
    assert dup.status_code == 409
    for i in range(4):
        r = client.post("/api/feedback", headers=h, json={"rating": 4, "category": "other", "message": f"note number {i}"})
        assert r.status_code == 201
    limited = client.post("/api/feedback", headers=h, json={"rating": 4, "category": "other", "message": "one too many"})
    assert limited.status_code == 429

    mine = client.get("/api/feedback/mine", headers=h).json()
    assert len(mine) == 5 and mine[-1]["message"] == "Add Rust questions!"
    wall = client.get("/api/feedback/recent").json()
    assert wall and wall[0]["author_name"] == "Linus"
    assert all("email" not in item for item in wall)
    assert "linus@example.com" not in str(wall)
