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


CORE = ["code_tracing", "debugging", "algorithmic_thinking", "edge_cases_testing", "code_review_design", "data_structures"]


def test_python_and_js_cover_every_core_domain_and_level():
    seen = {(q["domain"], q["difficulty"], q["language"]) for q in SEED_QUESTIONS}
    for d in CORE:
        for level in LEVELS:
            for lang in ("python", "javascript"):
                assert (d, level, lang) in seen


def test_all_languages_are_known():
    known = {lang["slug"] for lang in LANGUAGES}
    assert {q["language"] for q in SEED_QUESTIONS} <= known


def test_new_language_volume_per_level():
    counts = Counter((q["language"], q["difficulty"]) for q in SEED_QUESTIONS)
    for lang in ("html", "css", "php", "cpp"):
        for level in LEVELS:
            assert counts[(lang, level)] >= 6, (lang, level)


def test_markup_languages_skip_meaningless_domains():
    for q in SEED_QUESTIONS:
        if q["language"] in ("html", "css"):
            assert q["domain"] in {"fundamentals", "code_tracing", "debugging", "edge_cases_testing", "code_review_design"}, q["title"]


def test_logic_and_algorithms_volume():
    counts = Counter((q["domain"], q["difficulty"]) for q in SEED_QUESTIONS)
    for d in ("logic_problems", "algorithms"):
        for level in LEVELS:
            assert counts[(d, level)] >= 8, (d, level)
    assert all(q["language"] == "general" for q in SEED_QUESTIONS if q["domain"] == "logic_problems")
    algo_langs = {q["language"] for q in SEED_QUESTIONS if q["domain"] == "algorithms"}
    assert {"python", "javascript", "php", "general"} <= algo_langs


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


def test_fundamentals_volume_per_language_and_level():
    counts = Counter((q["language"], q["difficulty"]) for q in SEED_QUESTIONS if q["domain"] == "fundamentals")
    minimum = {"python": 8, "javascript": 8, "php": 8, "cpp": 8, "html": 6, "css": 6, "general": 5}
    for lang, n in minimum.items():
        for level in LEVELS:
            assert counts[(lang, level)] >= n, (lang, level, counts[(lang, level)])


def test_fundamentals_is_the_first_domain():
    assert DOMAINS[0]["slug"] == "fundamentals"


def test_cpp_covers_every_core_domain_level_and_algorithms():
    seen = {(q["domain"], q["difficulty"]) for q in SEED_QUESTIONS if q["language"] == "cpp"}
    for d in CORE + ["fundamentals"]:
        for level in LEVELS:
            assert (d, level) in seen, (d, level)
    assert {"beginner", "intermediate", "advanced"} <= {lvl for d, lvl in seen if d == "algorithms"}
    assert sum(1 for q in SEED_QUESTIONS if q["language"] == "cpp") >= 50
