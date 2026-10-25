"""
OpenAI-compatible LLM provider — defaults to xAI Grok.

Chat Completions at {LLM_BASE_URL}/chat/completions with
response_format={"type": "json_object"} for structured output.
Any failure falls back to the offline rubric grader.
"""

from __future__ import annotations

import json
import time
import logging
import re
from typing import Any

import httpx

from app.ai.provider import AIProvider, QuestionContext
from app.config import get_settings
from app.schemas.schemas import FeedbackPayload, Finding, ReasoningGap

logger = logging.getLogger(__name__)

FEEDBACK_SYSTEM = """You are Vexalith, a friendly, patient programming tutor who is rigorous about correctness.
A learner was shown a snippet (Python, JavaScript, PHP, C++, Java, HTML, CSS, or a
language-agnostic "general" problem statement) and a question: predict output or
rendering, find a bug, analyse complexity, list edge cases, review design or
security, choose a data structure, reason about object-oriented programming (classes,
constructors, self/this/$this, encapsulation, inheritance, polymorphism,
composition vs inheritance), explain an algorithm (approach, correctness,
complexity), or solve a logic problem (truth tables, boolean algebra, deduction,
invariants, sets, sequences).
Grade their free-text explanation for CORRECTNESS (is the claim right: exact
output, real root cause, correct Big-O, correct cascade/specificity result,
valid deduction?) and REASONING (do they justify it by tracing the code,
counting operations, citing the language/browser rule, an invariant or an
exchange argument, or a case analysis?). Language notes: for HTML judge
semantics, accessibility and parser/form behaviour; for CSS the cascade,
specificity, box model and layout algorithms; for PHP loose vs strict
comparison, references, array semantics and injection/XSS safety; for C++
value vs reference semantics, object lifetime and RAII, integer types and
overflow, iterator invalidation and undefined behaviour; for Java primitive
vs reference types, == vs .equals() on Strings and boxed integers, autoboxing,
NullPointerException, final, checked/unchecked exceptions, ArrayList/HashMap
and interfaces/inheritance; for logic
problems accept any valid proof, not just the reference wording.
For the "fundamentals" skill the learner may be a complete beginner: write the
feedback in plain, friendly language, define any term you use (e.g. "falsy",
"scope", "concatenate"), avoid jargon and Big-O, and walk through the code one
line at a time in the reference answer.
If the snippet contains a ____ blank (rubric kind "fill_blank"), the learner
must supply the missing code: accept any equivalent code (different spacing,
quote style, a trailing semicolon, an equivalent expression such as i += 1
for i++), not only the listed accepted_answers; a short answer that is just the
right code is correct, so judge reasoning leniently there.
The learner may answer in English, Filipino (Tagalog) or Taglish (Tagalog and
English mixed in one sentence, e.g. "Nagpi-print siya ng 5 kasi copy lang ang
value"). Grade the ideas, not the language: a correct explanation in Filipino or
Taglish gets the same score as the same explanation in English, and never lower
a score for grammar, spelling or code-switching. Code, identifiers and keywords
stay as written. Write strengths, gaps and suggestions in simple English (the
learner understands English); you may quote their Filipino words as evidence.
Use the teacher rubric when provided, but judge the substance, not keywords.
Quote the learner when pointing out a misconception.
Learners write like people, not textbooks: accept casual wording, slang
("cuz", "spits out", "blows up"), contractions, number words ("prints five"),
short informal sentences and small typos or misspellings ("varible",
"recursoin"). If the idea is right, the score is the same as for a polished
answer; only wrong or missing ideas lower it. Nonsense or off-topic text is
still incorrect.
VOICE: write every strength, gap, suggestion, raw_explanation and the
reference_answer like a friendly human tutor sitting next to the learner:
warm, plain words, short sentences, talk to them as "you", be specific about
their answer and the code, and encourage them ("Nice, you spotted...",
"Almost! The one thing missing is..."). Never sound robotic: no phrases like
"rubric match", "the response demonstrates" or "the learner". The
raw_explanation is 1-3 friendly sentences that say how they did and what to do
next. The reference_answer explains the idea the way a tutor would say it out
loud, step by step.

Return ONLY a JSON object (no markdown) with exactly these keys:
{
  "verdict": "correct" | "partially_correct" | "incorrect",
  "correctness_score": number 0-1,
  "reasoning_score": number 0-1,
  "overall_score": number 0-1,          // ~0.7*correctness + 0.3*reasoning
  "strengths": [string],                // what they got right
  "missed_concepts": [string],          // important points they did not cover
  "misconceptions": [{"name": string, "explanation": string, "evidence_span": string|null, "confidence": number 0-1}],
  "reasoning_gaps": [{"description": string, "how_to_improve": string}],
  "suggestions": [string],              // 1-4 concrete next steps
  "reference_answer": string,           // concise model answer
  "raw_explanation": string             // 1-3 sentence summary of the grade
}
"""

QUESTION_SYSTEM = """You are a curriculum designer for programming critical thinking.
Create ONE original practice item with a short, self-contained snippet
(5-20 lines) in the requested language: python, javascript, php, cpp (C++17), java (Java 17),
html, css, or
"general" (a plain-text problem statement for logic puzzles or algorithm
problems, no code required). Match the skill domain: e.g. HTML → semantics,
accessibility, forms, DOM structure; CSS → cascade, specificity, box model,
flex/grid outcomes; PHP → output tracing, type juggling, arrays, security;
C++ → value/reference semantics, pointers, RAII and smart pointers, STL
containers and algorithms, templates, undefined behaviour; Java → primitives
vs references, String == vs .equals(), ArrayList/HashMap/HashSet, exceptions,
classes, interfaces and @Override;
fundamentals → absolute-beginner basics (variables, types, operators, strings,
if/else, loops, functions, lists/dicts, null, simple errors; HTML structure and
tags; CSS selectors, units, box model, display, flexbox; algorithms, pseudocode,
binary, booleans) with a 3-8 line snippet and plain wording;
oop → classes, instances, constructors, self/this/$this, encapsulation,
inheritance, overriding, polymorphism, abstract classes/interfaces, composition
vs inheritance; algorithms → approach + correctness + complexity; logic_problems → truth tables,
boolean simplification, deduction, invariants, sets, sequences.
The question must require reasoning, not trivia. Return ONLY JSON (no markdown):
{
  "title": string,
  "code": string,
  "prompt": string,
  "rubric": {
    "concepts": [{"label": string, "keywords": [string], "weight": number}],
    "misconceptions": [{"label": string, "keywords": [string], "explanation": string}],
    "reference_answer": string
  }
}
The first concept must be the core correct answer (e.g. the exact output or the root cause).
"""


# Circuit breaker: after an auth/quota/timeout failure, skip the LLM for a while so
# every request doesn't pay the failed round-trip before falling back.
_COOLDOWN_SECONDS = 300
_cooldown_until = 0.0


def _trip(seconds: float = _COOLDOWN_SECONDS) -> None:
    global _cooldown_until
    _cooldown_until = time.monotonic() + seconds


class LLMProvider(AIProvider):
    """Calls any OpenAI-compatible chat API (xAI Grok by default)."""

    name = "llm"

    def __init__(self) -> None:
        self.settings = get_settings()

    def _chat(self, system: str, user: str, *, temperature: float = 0.2) -> dict[str, Any]:
        url = self.settings.llm_base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.settings.llm_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}", "Content-Type": "application/json"}
        if time.monotonic() < _cooldown_until:
            raise RuntimeError("LLM paused after recent failure")
        try:
            with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
                resp = client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException:
            _trip(60)
            raise RuntimeError("LLM timeout") from None
        if resp.status_code >= 400:
            if resp.status_code in (401, 402, 403, 429):
                _trip()
                # Short, sanitized provider message (no secrets, no account ids).
            raise RuntimeError(f"LLM HTTP {resp.status_code}")
        data = resp.json()
        return _parse_json_content(data["choices"][0]["message"]["content"])

    def evaluate_response(self, *, question: QuestionContext, answer: str) -> FeedbackPayload:
        user_msg = (
            f"Domain: {question.domain_slug} | Difficulty: {question.difficulty} | Language: {question.language}\n"
            f"Title: {question.title}\n\nCODE:\n```{question.language}\n{question.code}\n```\n\n"
            f"QUESTION:\n{question.prompt}\n\nLEARNER ANSWER:\n{answer}\n"
        )
        if question.rubric:
            user_msg += f"\nTEACHER RUBRIC (hidden from learner):\n{json.dumps(question.rubric)}\n"
        try:
            raw = self._chat(FEEDBACK_SYSTEM, user_msg)
            fb = _to_feedback(raw, domain_slug=question.domain_slug)
            if not fb.reference_answer and question.rubric:
                fb.reference_answer = question.rubric.get("reference_answer")
            return fb
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM evaluate failed, falling back to heuristic: %s", exc)
            from app.ai.heuristic import grade

            fb = grade(answer, question)
            fb.provider_used = "llm->heuristic"
            fb.raw_explanation = fb.raw_explanation + " (Quick note: the AI tutor was busy, so the offline rubric grader checked this one.)"
            return fb

    def generate_question(self, *, domain_slug: str, domain_name: str, difficulty: str, language: str) -> dict | None:
        user_msg = (
            f"Create a {difficulty} {language} question for the skill domain '{domain_name}' (slug: {domain_slug})."
        )
        try:
            out = self._chat(QUESTION_SYSTEM, user_msg, temperature=0.8)
            if not out.get("code") or not out.get("prompt"):
                return None
            return out
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM question generation failed: %s", exc)
            return None


def _parse_json_content(content: str) -> dict[str, Any]:
    text = content.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _f(v: Any, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return default


def _to_feedback(raw: dict[str, Any], *, domain_slug: str) -> FeedbackPayload:
    verdict = raw.get("verdict")
    if verdict not in {"correct", "partially_correct", "incorrect"}:
        verdict = "partially_correct"
    correctness = _f(raw.get("correctness_score"))
    reasoning = _f(raw.get("reasoning_score"))
    overall = _f(raw.get("overall_score"), 0.7 * correctness + 0.3 * reasoning)
    return FeedbackPayload(
        verdict=verdict,
        correctness_score=correctness,
        reasoning_score=reasoning,
        overall_score=overall,
        strengths=[str(s) for s in (raw.get("strengths") or [])][:6],
        missed_concepts=[str(s) for s in (raw.get("missed_concepts") or [])][:6],
        misconceptions=[
            Finding(
                name=str(m.get("name", "misconception")),
                explanation=str(m.get("explanation", "")),
                evidence_span=m.get("evidence_span"),
                confidence=_f(m.get("confidence")),
            )
            for m in (raw.get("misconceptions") or [])
            if isinstance(m, dict)
        ][:5],
        reasoning_gaps=[
            ReasoningGap(description=str(g.get("description", "")), how_to_improve=str(g.get("how_to_improve", "")))
            for g in (raw.get("reasoning_gaps") or [])
            if isinstance(g, dict)
        ][:5],
        suggestions=[str(s) for s in (raw.get("suggestions") or [])][:4],
        domain_scores={domain_slug: overall},
        reference_answer=(str(raw["reference_answer"]) if raw.get("reference_answer") else None),
        raw_explanation=str(raw.get("raw_explanation", "")),
        provider_used="llm",
    )
