"""
Abstract AI provider interface and factory.

Resolution order for feedback / generation:
1. LLMProvider  — if XAI_API_KEY or LLM_API_KEY is set (xAI Grok by default)
2. HFProvider   — if transformers+torch importable and hf_enabled
3. HeuristicProvider — always available offline fallback
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import lru_cache

from app.schemas.schemas import FeedbackPayload

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Contract every feedback / generation backend must satisfy."""

    name: str = "base"

    @abstractmethod
    def evaluate_response(
        self,
        *,
        scenario: str,
        prompt: str,
        answer: str,
        domain_slug: str,
        expected_signals: dict | None = None,
    ) -> FeedbackPayload:
        """Analyze a free-text answer and return structured, explainable feedback."""

    def generate_question(
        self,
        *,
        domain_slug: str,
        domain_name: str,
        difficulty: str,
    ) -> dict | None:
        """
        Optionally generate a new question dict:
        {title, scenario, prompt, expected_signals}.
        Return None if this provider cannot generate (caller uses seed bank).
        """
        return None


@lru_cache
def get_ai_provider() -> AIProvider:
    """Pick the best available provider once per process."""
    from app.config import get_settings

    settings = get_settings()

    if settings.llm_configured:
        from app.ai.llm_provider import LLMProvider

        logger.info("Using LLM provider (%s @ %s)", settings.llm_model, settings.llm_base_url)
        return LLMProvider()

    if settings.hf_enabled:
        try:
            from app.ai.hf_provider import HFProvider, is_hf_available

            if is_hf_available():
                logger.info("Using Hugging Face zero-shot provider")
                return HFProvider()
        except Exception as exc:  # noqa: BLE001
            logger.warning("HF provider unavailable: %s", exc)

    from app.ai.heuristic import HeuristicProvider

    logger.info("Using heuristic offline provider")
    return HeuristicProvider()


def hf_runtime_available() -> bool:
    """True if torch+transformers can be imported (model may not be downloaded yet)."""
    try:
        from app.ai.hf_provider import is_hf_available

        return is_hf_available()
    except Exception:  # noqa: BLE001
        return False
