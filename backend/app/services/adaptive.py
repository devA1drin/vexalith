"""
Adaptive learning engine.

Mastery model
-------------
Each (user, domain) pair stores mastery ∈ [0, 1].
After a scored attempt we apply an Elo-style update:

    expected = 1 / (1 + 10 ** ((difficulty_value - mastery) / 0.4))
    mastery  ← clamp(mastery + K * (score - expected), 0, 1)

Question selection
------------------
1. Choose the domain with the lowest mastery (weakest-first).
2. Map mastery → preferred difficulty band (beginner / intermediate / advanced).
3. Prefer an unseen question in that band; fall back to nearest band / any.
"""

from __future__ import annotations

from dataclasses import dataclass

# Difficulty midpoints used for Elo expected-score calculation.
DIFFICULTY_VALUE = {
    "beginner": 0.25,
    "intermediate": 0.55,
    "advanced": 0.85,
}

DIFFICULTY_ORDER = ("beginner", "intermediate", "advanced")


@dataclass(frozen=True)
class DomainMastery:
    domain_id: int
    domain_slug: str
    mastery: float
    attempts: int = 0


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def expected_success(mastery: float, difficulty: str) -> float:
    """Probability the learner succeeds given current mastery vs item difficulty."""
    d = DIFFICULTY_VALUE.get(difficulty, 0.55)
    return 1.0 / (1.0 + 10 ** ((d - mastery) / 0.4))


def update_mastery(
    mastery: float,
    score: float,
    difficulty: str,
    *,
    k: float = 0.15,
) -> float:
    """
    Elo-style Bayesian-ish update.

    Parameters
    ----------
    mastery : current estimate in [0, 1]
    score : observed performance in [0, 1] (from feedback.overall_score)
    difficulty : question difficulty label
    k : learning rate (larger = faster adaptation)
    """
    exp = expected_success(mastery, difficulty)
    return round(clamp(mastery + k * (score - exp)), 4)


def select_weakest_domain(masteries: list[DomainMastery]) -> DomainMastery:
    """Return the domain with the lowest mastery (ties → fewest attempts, then slug)."""
    if not masteries:
        raise ValueError("masteries list must not be empty")
    return sorted(masteries, key=lambda m: (m.mastery, m.attempts, m.domain_slug))[0]


def mastery_to_difficulty(mastery: float, *, offset: float = 0.05) -> str:
    """
    Map mastery to a target difficulty, slightly above current level (desirable difficulty).
    """
    target = clamp(mastery + offset)
    if target < 0.35:
        return "beginner"
    if target < 0.65:
        return "intermediate"
    return "advanced"


def pick_question(
    *,
    candidates: list[dict],
    seen_ids: set[int],
    preferred_difficulty: str,
) -> dict | None:
    """
    Pick the best question from candidate dicts.

    Each candidate: {id, difficulty, ...}
    Preference: unseen @ preferred → unseen @ adjacent → any unseen → any.
    """
    if not candidates:
        return None

    def band(diff: str) -> list[dict]:
        return [c for c in candidates if c["difficulty"] == diff]

    preferred_idx = DIFFICULTY_ORDER.index(preferred_difficulty)
    # Search order: preferred, then neighbors outward.
    order = [preferred_difficulty]
    for delta in (1, -1, 2, -2):
        idx = preferred_idx + delta
        if 0 <= idx < len(DIFFICULTY_ORDER):
            d = DIFFICULTY_ORDER[idx]
            if d not in order:
                order.append(d)

    # Pass 1: unseen in preferred bands
    for diff in order:
        unseen = [c for c in band(diff) if c["id"] not in seen_ids]
        if unseen:
            return unseen[0]

    # Pass 2: any unseen
    unseen_any = [c for c in candidates if c["id"] not in seen_ids]
    if unseen_any:
        return unseen_any[0]

    # Pass 3: recycle (prefer preferred difficulty)
    for diff in order:
        pool = band(diff)
        if pool:
            return pool[0]
    return candidates[0]
