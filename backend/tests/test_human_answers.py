"""Part 0: human-friendly prompts and a grader that understands casual human answers."""

from __future__ import annotations

import re

import pytest

from app.ai.casual import canonical, fuzzy_hit, tokens
from app.ai.heuristic import grade
from app.ai.provider import QuestionContext
from app.content.bank import SEED_QUESTIONS
from app.content.humanize import plain_prompt


def _ctx(q: dict) -> QuestionContext:
    return QuestionContext(q["title"], q["language"], q["code"], q["prompt"], q["domain"], q["difficulty"], q["rubric"])


def _q(title: str, language: str | None = None) -> dict:
    return next(q for q in SEED_QUESTIONS if q["title"] == title and (language is None or q["language"] == language))


def casualize(text: str) -> str:
    """Write a model answer the way a person might type it: lower case, slang, contractions, typos."""
    t = re.sub(r"\bbecause\b", "cuz", text)
    t = re.sub(r"\bdoes not\b", "doesn't", t)
    t = re.sub(r"\bis not\b", "isn't", t)
    t = re.sub(r"\bprints\b", "spits out", t)
    t = re.sub(r"\breturns\b", "gives back", t)

    def typo(m: re.Match) -> str:  # swap two letters in the middle of a long word
        w = m.group(0)
        i = len(w) // 2
        return w[:i] + w[i + 1] + w[i] + w[i + 2:]

    return re.sub(r"\b[a-z]{9,}\b", typo, t, count=2).lower()


# ── Prompts ──────────────────────────────────────────────────────────────────


def test_every_prompt_has_a_clear_task_line_and_guide():
    for q in SEED_QUESTIONS:
        question, _, task = q["prompt"].partition("\n\n")
        assert question.strip() and task.startswith("Your task: "), q["title"]
        guide = q["rubric"]["guide"]
        assert guide["look_for"] and "task" not in guide
        # "What counts" only for fill-in questions; explain questions get it from the task line.
        assert bool(guide["good_answer"]) == (q["rubric"].get("kind") == "fill_blank")
        # The task line never repeats the old one-size-fits-all sentence count.
        assert "2-4" not in task, q["title"]
        assert q["rubric"]["original_prompt"].strip()


def test_task_line_follows_what_the_question_asks():
    outputs = [q for q in SEED_QUESTIONS if q["domain"] == "fundamentals" and q["language"] == "python" and q["rubric"].get("kind") != "fill_blank" and "print" in q["prompt"].split("\n\n")[0]]
    assert outputs and all("exact output" in q["prompt"] for q in outputs)
    bugs = [q for q in SEED_QUESTIONS if q["domain"] == "debugging" and q["rubric"].get("kind") != "fill_blank"]
    assert bugs and all("name the bug" in q["prompt"] for q in bugs)
    assert len({q["prompt"].split("\n\n")[-1] for q in SEED_QUESTIONS}) >= 12


def test_fill_blank_prompts_say_to_type_only_the_code():
    for q in SEED_QUESTIONS:
        if q["rubric"].get("kind") == "fill_blank":
            assert "type only the code" in q["prompt"]


def test_terse_exam_wording_is_rewritten():
    assert plain_prompt("What is printed?") == "What does this code print?"
    assert plain_prompt("Which would you choose and why? Quantify.").endswith("how many steps or how much memory).")
    assert "Work out" in plain_prompt("Predict all four lines.")
    assert "how the amount of work grows" in plain_prompt("What is the Big-O?")
    allp = " ".join(q["prompt"] for q in SEED_QUESTIONS)
    for jargon in ("Quantify.", "What is logged?", "Predict "):
        assert jargon not in allp


def test_titles_are_unchanged_and_unique():
    keys = {(q["title"], q["language"]) for q in SEED_QUESTIONS}
    assert len(keys) == len(SEED_QUESTIONS) == 536


# ── Casual human answers ─────────────────────────────────────────────────────


def test_canonical_view_understands_everyday_wording():
    c = canonical("It doesn't change cuz it's a copy, it spits out five")
    assert "does not" in c and "because" in c and "it is" in c and "prints 5" in c
    assert "infinite loop" in canonical("the loop never ends lol")
    assert "did not change" in canonical("strip didnt change it")


def test_typos_match_but_unrelated_words_do_not():
    assert fuzzy_hit(tokens("the varible gets mutatted"), "variable")
    assert fuzzy_hit(tokens("the varible gets mutatted"), "mutat")
    assert fuzzy_hit(tokens("it's a referense"), "reference")
    assert not fuzzy_hit(tokens("lorem ipsum consectetur"), "const")
    assert not fuzzy_hit(tokens("banana"), "boolean")
    assert not fuzzy_hit(tokens("o(n^2)"), "o(n)")  # code-like keywords stay exact


def test_casual_answers_score_close_to_formal_ones_across_the_bank():
    gaps = []
    for q in SEED_QUESTIONS:
        if q["rubric"].get("kind") == "fill_blank":
            continue
        ref = q["rubric"]["reference_answer"]
        formal = grade(ref, _ctx(q)).overall_score
        casual = grade(casualize(ref), _ctx(q)).overall_score
        gaps.append(formal - casual)
    assert sum(gaps) / len(gaps) < 0.02
    assert sum(g > 0.15 for g in gaps) <= len(gaps) * 0.01


@pytest.mark.parametrize(
    "title,formal,casual",
    [
        (
            "Copying a value",
            "It prints 5. The assignment y = x copies the value 5, so changing x later does not change y.",
            "it spits out five cuz y just got a copy of x's value, so when x changes y doesn't care",
        ),
        (
            "Grade with elif",
            "It prints B. Python checks the conditions from top to bottom and stops at the first true one, so the rest are skipped.",
            "prints b. python checks the condiitons top to bottom and only the 1st true one runs, the rest get skipped",
        ),
    ],
)
def test_hand_written_casual_answers(title, formal, casual):
    q = _q(title, "python")
    f, c = grade(formal, _ctx(q)), grade(casual, _ctx(q))
    assert c.verdict == f.verdict == "correct"
    assert abs(f.correctness_score - c.correctness_score) <= 0.15


def test_casual_taglish_answer_still_counts():
    q = _q("Copying a value", "python")
    fb = grade("nagpi-print siya ng five kasi copy lang yung value ni x, kaya hindi nagbabago si y", _ctx(q))
    assert fb.verdict in ("correct", "partially_correct")
    assert fb.answer_language in ("fil", "taglish")


NONSENSE = [
    "banana purple sky dancing lol idk",
    "i dont know honestly no idea",
    "asdf qwerty zxcv lorem ipsum dolor sit amet consectetur",
    "the weather is nice today and i like pizza with pineapple",
]


def test_nonsense_still_fails_everywhere():
    for q in SEED_QUESTIONS:
        for text in NONSENSE:
            fb = grade(text, _ctx(q))
            assert fb.verdict == "incorrect" and fb.overall_score <= 0.3, (q["title"], text)


# ── Tutor voice ──────────────────────────────────────────────────────────────


def test_feedback_sounds_like_a_tutor():
    q = _q("Copying a value", "python")
    good = grade(q["rubric"]["reference_answer"], _ctx(q))
    bad = grade("no idea", _ctx(q))
    assert good.raw_explanation.startswith("Nice work")
    assert "Not quite yet" in bad.raw_explanation
    for fb in (good, bad):
        text = " ".join([fb.raw_explanation, *fb.suggestions, *(g.description for g in fb.reasoning_gaps)])
        assert "Rubric match" not in text and "Not addressed" not in text
