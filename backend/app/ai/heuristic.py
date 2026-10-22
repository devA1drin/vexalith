"""
Offline rubric-based grader for programming explanations.

Each seeded question stores a rubric:
  concepts:       [{label, keywords[], weight}]  ideas a correct answer contains
  misconceptions: [{label, keywords[], explanation}]
  reference_answer: str

Scoring (explainable):
  correctness = weighted share of rubric concepts mentioned (keyword/concept match)
  reasoning   = explanation quality: length + causal/technical reasoning markers
  overall     = 0.7 * correctness + 0.3 * reasoning − 0.12 per misconception
A misconception only counts when the primary concept was NOT hit, so an answer
that says "with let it would print 0 1 2" is not punished for mentioning it.
"""

from __future__ import annotations

import re

from app.ai.provider import AIProvider, QuestionContext
from app.schemas.schemas import FeedbackPayload, Finding, ReasoningGap

REASONING_MARKERS = re.compile(
    r"\b(because|since|therefore|so that|so the|which means|this means|thus|hence|as a result|"
    r"instead|however|whereas|otherwise|if|when|until|each|every|iteration|loop|complexity|"
    r"o\(|edge case|invariant|fix|should|returns?|throws?|raises?)\b",
    re.I,
)
_WS = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WS.sub(" ", text.lower()).strip()


def _despace(text: str) -> str:
    return _WS.sub("", text.lower())


def keyword_hit(answer_norm: str, answer_compact: str, keyword: str) -> bool:
    """Match a rubric keyword against the answer.

    Alphanumeric keywords match at a word start (so stems like 'mutat' work and
    '6' doesn't match '16'); keywords with symbols (e.g. '[1, 9]') also match
    with whitespace removed on both sides.
    """
    kw = keyword.lower().strip()
    if not kw:
        return False
    if re.fullmatch(r"[a-z0-9_ .'-]+", kw) and kw[0].isalnum():
        return re.search(r"(?<![a-z0-9])" + re.escape(kw), answer_norm) is not None
    return kw in answer_norm or _despace(kw) in answer_compact


def grade(answer: str, question: QuestionContext) -> FeedbackPayload:
    rubric = question.rubric or {}
    concepts = rubric.get("concepts") or []
    misconceptions_r = rubric.get("misconceptions") or []
    reference = rubric.get("reference_answer")

    norm = _normalize(answer)
    compact = _despace(answer)

    hit_labels: list[str] = []
    missed_labels: list[str] = []
    total_w = 0.0
    got_w = 0.0
    primary_hit = False
    for i, c in enumerate(concepts):
        w = float(c.get("weight", 1))
        total_w += w
        if any(keyword_hit(norm, compact, k) for k in c.get("keywords", [])):
            got_w += w
            hit_labels.append(c["label"])
            if i == 0:
                primary_hit = True
        else:
            missed_labels.append(c["label"])
    correctness = (got_w / total_w) if total_w else 0.5

    findings: list[Finding] = []
    if not primary_hit:
        for m in misconceptions_r:
            for k in m.get("keywords", []):
                if keyword_hit(norm, compact, k):
                    findings.append(
                        Finding(name=m["label"], explanation=m["explanation"], evidence_span=k, confidence=0.6)
                    )
                    break

    words = len(answer.split())
    length_score = min(1.0, words / 60.0)
    markers = len(REASONING_MARKERS.findall(answer))
    marker_score = min(1.0, markers / 5.0)
    reasoning = round(0.5 * length_score + 0.5 * marker_score, 3)

    overall = 0.7 * correctness + 0.3 * reasoning - 0.12 * len(findings)
    overall = round(max(0.0, min(1.0, overall)), 3)
    correctness = round(correctness, 3)

    if correctness >= 0.75 and not findings:
        verdict = "correct"
    elif correctness >= 0.35:
        verdict = "partially_correct"
    else:
        verdict = "incorrect"

    gaps: list[ReasoningGap] = []
    if words < 20:
        gaps.append(ReasoningGap(
            description="The explanation is very short.",
            how_to_improve="State your answer, then justify it step by step (what the code does on each relevant line).",
        ))
    if marker_score < 0.4:
        gaps.append(ReasoningGap(
            description="Little explicit causal reasoning (because / so / therefore / when ...).",
            how_to_improve="Connect each claim to the code: 'X happens because line N does Y'.",
        ))
    for label in missed_labels[:3]:
        gaps.append(ReasoningGap(description=f"Not addressed: {label}.", how_to_improve=f"Explain {label} explicitly."))

    suggestions: list[str] = []
    if findings:
        suggestions.append("Re-trace the code line by line; your answer matches a common misconception.")
    if missed_labels:
        suggestions.append("Cover the missing points: " + "; ".join(missed_labels[:3]) + ".")
    if question.domain_slug == "fundamentals":
        suggestions.append(
            "Beginner tip: say what each line does in plain words, write down the value of every variable "
            "after each step, then compare with the model answer below."
        )
    elif question.domain_slug == "algorithmic_thinking":
        suggestions.append("Justify Big-O by counting how many times the dominant operation runs.")
    elif question.domain_slug == "edge_cases_testing":
        suggestions.append("For each edge case, state the input, the expected result, and the actual result.")
    elif question.domain_slug == "debugging":
        suggestions.append("Name the root cause, show a failing input, and give the corrected code.")
    if not suggestions:
        suggestions.append("Great work — try explaining an alternative approach and its tradeoffs.")

    explanation = (
        f"Rubric match: {len(hit_labels)}/{len(concepts)} key points "
        f"(correctness {correctness:.0%}); reasoning quality {reasoning:.0%}"
        + (f"; {len(findings)} misconception(s) detected." if findings else ".")
    )
    return FeedbackPayload(
        verdict=verdict,
        correctness_score=correctness,
        reasoning_score=reasoning,
        overall_score=overall,
        strengths=[f"Covered: {h}" for h in hit_labels],
        missed_concepts=missed_labels,
        misconceptions=findings,
        reasoning_gaps=gaps[:4],
        suggestions=suggestions[:4],
        domain_scores={question.domain_slug: overall},
        reference_answer=reference,
        raw_explanation=explanation,
        provider_used="heuristic",
    )


class HeuristicProvider(AIProvider):
    name = "heuristic"

    def evaluate_response(self, *, question: QuestionContext, answer: str) -> FeedbackPayload:
        return grade(answer, question)
