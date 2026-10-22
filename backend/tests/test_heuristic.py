"""Offline rubric grader (no network)."""

from app.ai.heuristic import HeuristicProvider, keyword_hit
from app.ai.provider import QuestionContext
from app.content.bank import SEED_QUESTIONS


def _ctx(title: str, language: str) -> QuestionContext:
    item = next(q for q in SEED_QUESTIONS if q["title"] == title and q["language"] == language)
    return QuestionContext(
        title=item["title"], language=item["language"], code=item["code"], prompt=item["prompt"],
        domain_slug=item["domain"], difficulty=item["difficulty"], rubric=item["rubric"],
    )


def test_keyword_matching_rules():
    assert keyword_hit("it prints 6 because", "itprints6because", "6")
    assert not keyword_hit("it prints 16", "itprints16", "6")
    assert keyword_hit("you are mutating the list", "youaremutatingthelist", "mutat")
    assert keyword_hit("result is [1,9]", "resultis[1,9]", "[1, 9]")


def test_correct_tracing_answer_scores_high():
    q = _ctx("Mutable default argument", "python")
    fb = HeuristicProvider().evaluate_response(
        question=q,
        answer=("The first call prints [1] and the second prints [1, 2] because the default list is "
                "evaluated once when the function is defined, so every call shares the same list."),
    )
    assert fb.verdict == "correct"
    assert fb.correctness_score >= 0.99
    assert fb.misconceptions == []
    assert fb.reference_answer


def test_misconception_detected_and_scored_lower():
    q = _ctx("Mutable default argument", "python")
    good = HeuristicProvider().evaluate_response(
        question=q, answer="Prints [1] then [1, 2] since the mutable default list is shared between calls.")
    bad = HeuristicProvider().evaluate_response(
        question=q, answer="It prints [1] and then [2] because each call gets a new empty list.")
    assert bad.misconceptions and bad.misconceptions[0].evidence_span == "[2]"
    assert bad.verdict == "incorrect"
    assert good.overall_score > bad.overall_score


def test_misconception_not_flagged_when_core_answer_right():
    q = _ctx("var in a loop with setTimeout", "javascript")
    fb = HeuristicProvider().evaluate_response(
        question=q,
        answer=("It logs 3 three times because var is function-scoped and the callbacks run after the loop "
                "finishes; with let it prints 0 1 2."),
    )
    assert fb.misconceptions == []
    assert fb.verdict == "correct"


def test_short_answer_has_reasoning_gaps():
    q = _ctx("Naive Fibonacci", "python")
    fb = HeuristicProvider().evaluate_response(question=q, answer="It is slow.")
    assert fb.verdict == "incorrect"
    assert fb.reasoning_gaps
    assert fb.missed_concepts
