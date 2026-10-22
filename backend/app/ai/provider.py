"""
Abstract grader interface and factory.

Resolution order:
1. LLMProvider       — if XAI_API_KEY / LLM_API_KEY is set (xAI Grok by default);
                       falls back to the heuristic grader on any runtime error.
2. HeuristicProvider — offline rubric/keyword grader, always available.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache

from app.schemas.schemas import FeedbackPayload

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QuestionContext:
    title: str
    language: str
    code: str
    prompt: str
    domain_slug: str
    difficulty: str
    rubric: dict | None = None


class AIProvider(ABC):
    """Contract every grading / generation backend must satisfy."""

    name: str = "base"

    @abstractmethod
    def evaluate_response(self, *, question: QuestionContext, answer: str) -> FeedbackPayload:
        """Grade a free-text explanation and return structured, explainable feedback."""

    def generate_question(
        self,
        *,
        domain_slug: str,
        domain_name: str,
        difficulty: str,
        language: str,
    ) -> dict | None:
        """Optionally generate {title, code, prompt, rubric}. None → use the seed bank."""
        return None


@lru_cache
def get_ai_provider() -> AIProvider:
    from app.config import get_settings

    settings = get_settings()
    if settings.llm_configured:
        from app.ai.llm_provider import LLMProvider

        logger.info("Using LLM provider (%s @ %s)", settings.llm_model, settings.llm_base_url)
        return LLMProvider()

    from app.ai.heuristic import HeuristicProvider

    logger.info("Using heuristic offline provider")
    return HeuristicProvider()
