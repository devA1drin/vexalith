"""Unit tests for the adaptive mastery / selection engine (no DB / network)."""

import pytest

from app.services.adaptive import (
    DomainMastery,
    expected_success,
    mastery_to_difficulty,
    pick_question,
    select_weakest_domain,
    update_mastery,
)


def test_expected_success_higher_when_mastery_above_difficulty():
    easy = expected_success(0.8, "beginner")
    hard = expected_success(0.2, "advanced")
    assert easy > 0.7
    assert hard < 0.3


def test_update_mastery_increases_on_strong_performance():
    before = 0.5
    after = update_mastery(before, score=0.95, difficulty="intermediate", k=0.2)
    assert after > before


def test_update_mastery_decreases_on_weak_performance():
    before = 0.5
    after = update_mastery(before, score=0.1, difficulty="intermediate", k=0.2)
    assert after < before


def test_update_mastery_clamped():
    assert update_mastery(0.99, score=1.0, difficulty="beginner", k=0.5) <= 1.0
    assert update_mastery(0.01, score=0.0, difficulty="advanced", k=0.5) >= 0.0


def test_select_weakest_domain():
    domains = [
        DomainMastery(1, "a", 0.7, 3),
        DomainMastery(2, "b", 0.3, 1),
        DomainMastery(3, "c", 0.5, 2),
    ]
    assert select_weakest_domain(domains).domain_slug == "b"


def test_select_weakest_ties_break_on_attempts():
    domains = [
        DomainMastery(1, "a", 0.4, 5),
        DomainMastery(2, "b", 0.4, 1),
    ]
    assert select_weakest_domain(domains).domain_slug == "b"


def test_select_weakest_empty_raises():
    with pytest.raises(ValueError):
        select_weakest_domain([])


@pytest.mark.parametrize(
    "mastery,expected",
    [
        (0.1, "beginner"),
        (0.4, "intermediate"),
        (0.7, "advanced"),
    ],
)
def test_mastery_to_difficulty(mastery, expected):
    assert mastery_to_difficulty(mastery, offset=0.05) == expected


def test_pick_question_prefers_unseen_at_target_difficulty():
    candidates = [
        {"id": 1, "difficulty": "beginner"},
        {"id": 2, "difficulty": "intermediate"},
        {"id": 3, "difficulty": "advanced"},
        {"id": 4, "difficulty": "intermediate"},
    ]
    picked = pick_question(
        candidates=candidates,
        seen_ids={2},
        preferred_difficulty="intermediate",
    )
    assert picked is not None
    assert picked["id"] == 4
    assert picked["difficulty"] == "intermediate"


def test_pick_question_falls_back_to_adjacent_band():
    candidates = [
        {"id": 1, "difficulty": "beginner"},
        {"id": 2, "difficulty": "advanced"},
    ]
    picked = pick_question(
        candidates=candidates,
        seen_ids=set(),
        preferred_difficulty="intermediate",
    )
    assert picked is not None
    assert picked["difficulty"] in {"beginner", "advanced"}


def test_pick_question_recycles_when_all_seen():
    candidates = [
        {"id": 1, "difficulty": "beginner"},
        {"id": 2, "difficulty": "intermediate"},
    ]
    picked = pick_question(
        candidates=candidates,
        seen_ids={1, 2},
        preferred_difficulty="intermediate",
    )
    assert picked is not None
    assert picked["id"] == 2
