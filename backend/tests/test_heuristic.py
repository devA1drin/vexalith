"""Smoke tests for offline heuristic feedback (no network)."""

from app.ai.heuristic import HeuristicProvider


def test_heuristic_detects_ad_hominem():
    provider = HeuristicProvider()
    fb = provider.evaluate_response(
        scenario="A debate about policy.",
        prompt="Analyze the argument.",
        answer="Jordan is an idiot so we should ignore the proposal entirely.",
        domain_slug="fallacy_detection",
    )
    names = [f.name for f in fb.fallacies]
    assert "ad_hominem" in names
    assert 0.0 <= fb.overall_score <= 1.0
    assert fb.provider_used == "heuristic"


def test_heuristic_rewards_structured_reasoning():
    provider = HeuristicProvider()
    weak = provider.evaluate_response(
        scenario="s",
        prompt="p",
        answer="I disagree.",
        domain_slug="argument_analysis",
    )
    strong = provider.evaluate_response(
        scenario="s",
        prompt="p",
        answer=(
            "The main claim is unsupported because the evidence is correlational. "
            "A key assumption is that no confounders exist. However, an alternative "
            "explanation is seasonal demand. Therefore we should gather better warrants "
            "before accepting the causal premise."
        ),
        domain_slug="argument_analysis",
        expected_signals={"good_keywords": ["assumption", "evidence", "alternative"], "fallacy_traps": []},
    )
    assert strong.overall_score > weak.overall_score
