"""
Offline Hugging Face zero-shot fallacy detector.

Uses facebook/bart-large-mnli (or configured model) via transformers pipeline.
The model is loaded lazily on first use so import/startup stays fast.
If torch/transformers are missing, callers should skip this provider.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from app.ai.provider import AIProvider
from app.config import get_settings
from app.schemas.schemas import FallacyFinding, FeedbackPayload, ReasoningGap

logger = logging.getLogger(__name__)

FALLACY_LABELS = [
    "ad hominem attack",
    "straw man argument",
    "false dilemma",
    "slippery slope",
    "circular reasoning",
    "hasty generalization",
    "appeal to authority",
    "post hoc causal claim",
    "red herring",
    "bandwagon appeal",
    "sound logical reasoning",
]

_LABEL_TO_NAME = {
    "ad hominem attack": "ad_hominem",
    "straw man argument": "straw_man",
    "false dilemma": "false_dilemma",
    "slippery slope": "slippery_slope",
    "circular reasoning": "circular_reasoning",
    "hasty generalization": "hasty_generalization",
    "appeal to authority": "appeal_to_authority",
    "post hoc causal claim": "post_hoc",
    "red herring": "red_herring",
    "bandwagon appeal": "bandwagon",
    "sound logical reasoning": "sound_reasoning",
}

_pipeline: Any = None
_pipeline_lock = threading.Lock()
_pipeline_failed = False


def is_hf_available() -> bool:
    """Return True if torch and transformers can be imported."""
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401

        return True
    except ImportError:
        return False


def _get_pipeline() -> Any | None:
    """Lazy-load the zero-shot classification pipeline (once)."""
    global _pipeline, _pipeline_failed
    if _pipeline is not None:
        return _pipeline
    if _pipeline_failed:
        return None

    with _pipeline_lock:
        if _pipeline is not None:
            return _pipeline
        if _pipeline_failed:
            return None
        try:
            from transformers import pipeline

            settings = get_settings()
            logger.info("Loading HF model %s (may take a while on first run)…", settings.hf_model_name)
            _pipeline = pipeline(
                "zero-shot-classification",
                model=settings.hf_model_name,
            )
            logger.info("HF model ready")
            return _pipeline
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load HF model: %s — heuristic path will be used", exc)
            _pipeline_failed = True
            return None


class HFProvider(AIProvider):
    """Zero-shot fallacy detection + heuristic scoring."""

    name = "hf"

    def evaluate_response(
        self,
        *,
        scenario: str,
        prompt: str,
        answer: str,
        domain_slug: str,
        expected_signals: dict | None = None,
    ) -> FeedbackPayload:
        from app.ai.heuristic import HeuristicProvider, score_answer_heuristically

        clf = _get_pipeline()
        if clf is None:
            # Graceful degradation when model download fails / is too slow.
            fb = HeuristicProvider().evaluate_response(
                scenario=scenario,
                prompt=prompt,
                answer=answer,
                domain_slug=domain_slug,
                expected_signals=expected_signals,
            )
            fb.provider_used = "hf->heuristic"
            return fb

        # Classify the answer against fallacy labels (multi-label).
        result = clf(answer, FALLACY_LABELS, multi_label=True)
        fallacies: list[FallacyFinding] = []
        sound_score = 0.0
        for label, score in zip(result["labels"], result["scores"], strict=False):
            name = _LABEL_TO_NAME.get(label, label)
            if name == "sound_reasoning":
                sound_score = float(score)
                continue
            if float(score) >= 0.35:
                fallacies.append(
                    FallacyFinding(
                        name=name,
                        explanation=(
                            f"Zero-shot classifier assigned {score:.0%} confidence that the "
                            f"answer exhibits '{label}'."
                        ),
                        evidence_span=None,
                        confidence=round(float(score), 3),
                    )
                )

        base = score_answer_heuristically(
            answer=answer,
            domain_slug=domain_slug,
            expected_signals=expected_signals,
        )
        # Blend HF soundness with heuristic length/keyword score.
        overall = round(0.55 * sound_score + 0.45 * base["overall_score"], 3)
        # Penalize for detected fallacies.
        overall = max(0.05, overall - 0.08 * len(fallacies))

        gaps = base["reasoning_gaps"]
        if fallacies and not gaps:
            gaps = [
                ReasoningGap(
                    description="Potential logical fallacies were detected in the argument.",
                    how_to_improve="Revisit each flagged pattern and rewrite the claim with clearer warrants.",
                )
            ]

        return FeedbackPayload(
            fallacies=fallacies,
            reasoning_gaps=gaps,
            domain_scores={domain_slug: overall},
            suggestions=base["suggestions"],
            overall_score=overall,
            raw_explanation=(
                f"HF zero-shot soundness={sound_score:.2f}; "
                f"heuristic={base['overall_score']:.2f}; blended={overall:.2f}."
            ),
            provider_used="hf",
        )
