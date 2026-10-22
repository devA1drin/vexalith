"""The LLM provider must fall back fast and stop calling a provider that rejects the key."""

import httpx

from app.ai import llm_provider
from app.ai.provider import QuestionContext


class _Resp:
    status_code = 403

    def json(self):
        return {}


def test_403_trips_breaker_and_falls_back(monkeypatch):
    calls = {"n": 0}

    def fake_post(self, url, headers=None, json=None):  # noqa: A002
        calls["n"] += 1
        return _Resp()

    monkeypatch.setattr(httpx.Client, "post", fake_post)
    monkeypatch.setattr(llm_provider, "_cooldown_until", 0.0)
    prov = llm_provider.LLMProvider()
    q = QuestionContext(
        domain_slug="code_tracing", difficulty="beginner", language="python", title="t",
        code="print(1)", prompt="What prints?",
        rubric={"concepts": [{"label": "prints 1", "keywords": ["1"], "weight": 1}], "misconceptions": [], "reference_answer": "1"},
    )
    a = prov.evaluate_response(question=q, answer="It prints 1 because print outputs its argument.")
    b = prov.evaluate_response(question=q, answer="It prints 1 because print outputs its argument.")
    assert a.provider_used == b.provider_used == "llm->heuristic"
    assert calls["n"] == 1  # second call skipped by the breaker
    assert "403" not in (a.raw_explanation or "")
