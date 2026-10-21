"""
OpenAI-compatible LLM provider — defaults to xAI Grok.

Uses Chat Completions at {LLM_BASE_URL}/chat/completions with
response_format={"type":"json_object"} for structured feedback JSON.
See https://docs.x.ai/developers/model-capabilities/text/structured-outputs
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.ai.provider import AIProvider
from app.config import get_settings
from app.schemas.schemas import FallacyFinding, FeedbackPayload, ReasoningGap

logger = logging.getLogger(__name__)

FEEDBACK_SYSTEM = """You are an expert critical-thinking tutor.
Analyze the student's free-text answer to a scenario-based question.
Return ONLY valid JSON matching this schema (no markdown fences):
{
  "fallacies": [{"name": str, "explanation": str, "evidence_span": str|null, "confidence": 0-1}],
  "reasoning_gaps": [{"description": str, "how_to_improve": str}],
  "domain_scores": {"<domain_slug>": 0-1, ...},
  "suggestions": [str],
  "overall_score": 0-1,
  "raw_explanation": str
}
Be specific, cite phrases from the answer when calling out fallacies, and be encouraging but rigorous.
Common fallacies: ad_hominem, straw_man, false_dilemma, slippery_slope, circular_reasoning,
hasty_generalization, appeal_to_authority, post_hoc, red_herring, bandwagon, anecdotal.
"""

QUESTION_SYSTEM = """You are an expert curriculum designer for critical thinking.
Generate ONE original practice scenario as JSON only (no markdown):
{
  "title": str,
  "scenario": str (2-4 paragraphs of realistic context),
  "prompt": str (open-ended question asking the student to analyze/argue),
  "expected_signals": {"good_keywords": [str], "fallacy_traps": [str]}
}
"""


class LLMProvider(AIProvider):
    """Calls any OpenAI-compatible chat API (xAI Grok by default)."""

    name = "llm"

    def __init__(self) -> None:
        self.settings = get_settings()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }

    def _chat(self, system: str, user: str, *, temperature: float = 0.4) -> dict[str, Any]:
        url = self.settings.llm_base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            # xAI supports json_object and json_schema structured outputs.
            "response_format": {"type": "json_object"},
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            if resp.status_code >= 400:
                # Surface provider message (e.g. xAI credits exhausted) without leaking secrets.
                detail = resp.text[:500]
                raise RuntimeError(f"LLM HTTP {resp.status_code}: {detail}")
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_json_content(content)

    def evaluate_response(
        self,
        *,
        scenario: str,
        prompt: str,
        answer: str,
        domain_slug: str,
        expected_signals: dict | None = None,
    ) -> FeedbackPayload:
        user_msg = (
            f"Domain focus: {domain_slug}\n\n"
            f"SCENARIO:\n{scenario}\n\n"
            f"QUESTION:\n{prompt}\n\n"
            f"STUDENT ANSWER:\n{answer}\n"
        )
        if expected_signals:
            user_msg += f"\nTeacher signals (optional hints): {json.dumps(expected_signals)}\n"

        try:
            raw = self._chat(FEEDBACK_SYSTEM, user_msg)
            return _to_feedback(raw, domain_slug=domain_slug, provider="llm")
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM evaluate failed, falling back to heuristic: %s", exc)
            from app.ai.heuristic import HeuristicProvider

            fb = HeuristicProvider().evaluate_response(
                scenario=scenario,
                prompt=prompt,
                answer=answer,
                domain_slug=domain_slug,
                expected_signals=expected_signals,
            )
            fb.provider_used = "llm->heuristic"
            fb.raw_explanation = f"LLM error ({exc}); used heuristic. " + fb.raw_explanation
            return fb

    def generate_question(
        self,
        *,
        domain_slug: str,
        domain_name: str,
        difficulty: str,
    ) -> dict | None:
        user_msg = (
            f"Create a {difficulty}-difficulty question targeting the skill domain "
            f"'{domain_name}' (slug: {domain_slug})."
        )
        try:
            return self._chat(QUESTION_SYSTEM, user_msg, temperature=0.8)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM question generation failed: %s", exc)
            return None


def _parse_json_content(content: str) -> dict[str, Any]:
    """Parse model output, tolerating accidental markdown fences."""
    text = content.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _to_feedback(raw: dict[str, Any], *, domain_slug: str, provider: str) -> FeedbackPayload:
    fallacies = [
        FallacyFinding(
            name=str(f.get("name", "unknown")),
            explanation=str(f.get("explanation", "")),
            evidence_span=f.get("evidence_span"),
            confidence=float(f.get("confidence", 0.5)),
        )
        for f in (raw.get("fallacies") or [])
        if isinstance(f, dict)
    ]
    gaps = [
        ReasoningGap(
            description=str(g.get("description", "")),
            how_to_improve=str(g.get("how_to_improve", "")),
        )
        for g in (raw.get("reasoning_gaps") or [])
        if isinstance(g, dict)
    ]
    scores = raw.get("domain_scores") or {}
    if domain_slug not in scores:
        scores[domain_slug] = float(raw.get("overall_score", 0.5))
    return FeedbackPayload(
        fallacies=fallacies,
        reasoning_gaps=gaps,
        domain_scores={k: float(v) for k, v in scores.items()},
        suggestions=[str(s) for s in (raw.get("suggestions") or [])],
        overall_score=float(raw.get("overall_score", 0.5)),
        raw_explanation=str(raw.get("raw_explanation", "")),
        provider_used=provider,
    )
