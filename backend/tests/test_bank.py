"""Question bank integrity."""

from collections import Counter

from app.content.bank import SEED_QUESTIONS
from app.content.domains import DOMAINS, LANGUAGES

LEVELS = {"beginner", "intermediate", "advanced"}


def test_every_domain_level_has_at_least_four_questions():
    counts = Counter((q["domain"], q["difficulty"]) for q in SEED_QUESTIONS)
    for d in DOMAINS:
        for level in LEVELS:
            assert counts[(d["slug"], level)] >= 4, (d["slug"], level)


def test_both_languages_covered_per_domain_and_level():
    langs = {lang["slug"] for lang in LANGUAGES}
    seen = {(q["domain"], q["difficulty"], q["language"]) for q in SEED_QUESTIONS}
    for d in DOMAINS:
        for level in LEVELS:
            for lang in langs:
                assert (d["slug"], level, lang) in seen


def test_rubrics_are_well_formed_and_titles_unique():
    titles = Counter((q["title"], q["language"]) for q in SEED_QUESTIONS)
    assert max(titles.values()) == 1
    for q in SEED_QUESTIONS:
        assert q["code"].strip() and q["prompt"].strip()
        r = q["rubric"]
        assert r["reference_answer"]
        assert r["concepts"] and all(c["keywords"] for c in r["concepts"])


def test_reference_answers_pass_their_own_rubric():
    from app.ai.heuristic import grade
    from app.ai.provider import QuestionContext

    for q in SEED_QUESTIONS:
        ctx = QuestionContext(q["title"], q["language"], q["code"], q["prompt"], q["domain"], q["difficulty"], q["rubric"])
        fb = grade(q["rubric"]["reference_answer"], ctx)
        assert fb.correctness_score >= 0.75 and not fb.misconceptions, q["title"]
