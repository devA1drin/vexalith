"""
Always-available offline evaluator.

Uses keyword/length heuristics + optional expected_signals from the question bank.
No ML dependencies required — used when LLM and HF are unavailable, and as a
safety net when they fail at runtime.
"""

from __future__ import annotations

import re

from app.ai.provider import AIProvider
from app.schemas.schemas import FallacyFinding, FeedbackPayload, ReasoningGap

# Lightweight keyword → fallacy mapping for demo / portfolio purposes.
FALLACY_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("ad_hominem", "Attacks the person rather than the argument.",
     re.compile(r"\b(idiot|stupid|moron|because (he|she|they) (is|are))\b", re.I)),
    ("slippery_slope", "Assumes a chain of increasingly extreme consequences without evidence.",
     re.compile(r"\b(will (inevitably|eventually) lead|slippery slope|next thing you know)\b", re.I)),
    ("false_dilemma", "Presents only two options when more exist.",
     re.compile(r"\b(either .+ or |only two (choices|options)|must choose between)\b", re.I)),
    ("hasty_generalization", "Draws a broad conclusion from too little evidence.",
     re.compile(r"\b(all|everyone|nobody|always|never)\b.{0,40}\b(are|is|do|does)\b", re.I)),
    ("appeal_to_authority", "Relies on authority without relevant expertise or evidence.",
     re.compile(r"\b(experts say|as (everyone|they) know|trust (me|them) because)\b", re.I)),
    ("bandwagon", "Argues something is true because many people believe it.",
     re.compile(r"\b(everyone (knows|thinks|agrees)|most people|popular opinion)\b", re.I)),
    ("circular_reasoning", "Uses the conclusion as a premise.",
     re.compile(r"\b(because it('?s| is) true|true because|obviously true)\b", re.I)),
    ("post_hoc", "Assumes causation from temporal sequence alone.",
     re.compile(r"\b(after .+ therefore|caused by|because (of )?(this|that) happened)\b", re.I)),
]

QUALITY_MARKERS = re.compile(
    r"\b(because|therefore|however|evidence|assume|assumption|premise|warrant|"
    r"counterargument|alternative|causal|correlation|bias|fallacy|support)\b",
    re.I,
)


def score_answer_heuristically(
    *,
    answer: str,
    domain_slug: str,
    expected_signals: dict | None = None,
) -> dict:
    """Shared scoring used by HeuristicProvider and HFProvider blend."""
    words = answer.split()
    length_score = min(1.0, len(words) / 120.0)  # ~120 words ≈ full credit for length
    marker_hits = len(QUALITY_MARKERS.findall(answer))
    marker_score = min(1.0, marker_hits / 6.0)

    good_bonus = 0.0
    if expected_signals:
        goods = [g.lower() for g in expected_signals.get("good_keywords", [])]
        hits = sum(1 for g in goods if g in answer.lower())
        if goods:
            good_bonus = 0.25 * (hits / len(goods))

    fallacies: list[FallacyFinding] = []
    for name, expl, pattern in FALLACY_PATTERNS:
        m = pattern.search(answer)
        if m:
            fallacies.append(
                FallacyFinding(
                    name=name,
                    explanation=expl,
                    evidence_span=m.group(0)[:120],
                    confidence=0.55,
                )
            )

    # Trap keywords from seed bank
    if expected_signals:
        for trap in expected_signals.get("fallacy_traps", []):
            if trap.lower() in answer.lower() and not any(f.name == trap for f in fallacies):
                fallacies.append(
                    FallacyFinding(
                        name=trap,
                        explanation=f"Answer echoes a common '{trap}' trap for this scenario.",
                        evidence_span=trap,
                        confidence=0.45,
                    )
                )

    overall = 0.45 * length_score + 0.35 * marker_score + good_bonus
    overall = max(0.05, overall - 0.1 * len(fallacies))
    overall = round(min(1.0, overall), 3)

    gaps: list[ReasoningGap] = []
    if length_score < 0.4:
        gaps.append(
            ReasoningGap(
                description="The response is quite short for an open-ended critical analysis.",
                how_to_improve="Aim for a clear claim, at least one supporting reason, and a consideration of alternatives.",
            )
        )
    if marker_score < 0.3:
        gaps.append(
            ReasoningGap(
                description="Limited use of explicit reasoning language (because, evidence, assumption, etc.).",
                how_to_improve="Make warrants explicit: state why evidence supports the claim and name assumptions.",
            )
        )
    if not gaps and overall < 0.6:
        gaps.append(
            ReasoningGap(
                description="The argument could engage more deeply with counter-evidence.",
                how_to_improve="Steelman the opposing view, then explain why your position still holds.",
            )
        )

    suggestions = [
        "State your main claim in one sentence, then list supporting reasons.",
        "Name at least one assumption your argument depends on.",
        "Consider an alternative explanation and why it is less plausible.",
    ]
    if fallacies:
        suggestions.insert(0, f"Revise passages that triggered: {', '.join(f.name for f in fallacies)}.")

    return {
        "fallacies": fallacies,
        "reasoning_gaps": gaps,
        "overall_score": overall,
        "suggestions": suggestions[:4],
        "domain_scores": {domain_slug: overall},
    }


class HeuristicProvider(AIProvider):
    name = "heuristic"

    def evaluate_response(
        self,
        *,
        scenario: str,
        prompt: str,
        answer: str,
        domain_slug: str,
        expected_signals: dict | None = None,
    ) -> FeedbackPayload:
        result = score_answer_heuristically(
            answer=answer,
            domain_slug=domain_slug,
            expected_signals=expected_signals,
        )
        return FeedbackPayload(
            fallacies=result["fallacies"],
            reasoning_gaps=result["reasoning_gaps"],
            domain_scores=result["domain_scores"],
            suggestions=result["suggestions"],
            overall_score=result["overall_score"],
            raw_explanation=(
                "Offline heuristic evaluation (keyword patterns + structure markers). "
                "Configure XAI_API_KEY for Grok-powered feedback."
            ),
            provider_used="heuristic",
        )
