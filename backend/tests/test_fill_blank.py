"""Fill-in-the-missing-code question type: helper, matching and grading."""

import pytest

from app.ai.heuristic import fill_blank_hit, grade
from app.ai.provider import QuestionContext
from app.content.qdef import BLANK, FB


def _q():
    return FB("fundamentals", "beginner", "cpp", "Loop until three",
              "for (int i = 0; ____; i++) {\n    std::cout << i;\n}",
              "Fill in the condition so the loop prints 012.",
              ["i < 3", "i <= 2", "3 > i"],
              [("the loop stops once i reaches 3", ["reaches 3", "stops", "3 < 3"], 1)],
              [("uses <= 3", ["i <= 3"], "i <= 3 also prints 3.")],
              "The blank is i < 3: the loop stops when i reaches 3 because 3 < 3 is false.")


def _ctx(q):
    return QuestionContext(q["title"], q["language"], q["code"], q["prompt"], q["domain"], q["difficulty"], q["rubric"])


def test_helper_builds_a_fill_blank_rubric():
    q = _q()
    assert q["code"].count(BLANK) == 1
    assert q["rubric"]["kind"] == "fill_blank"
    assert q["rubric"]["accepted_answers"] == ["i < 3", "i <= 2", "3 > i"]
    assert q["rubric"]["concepts"][0]["keywords"] == ["i < 3", "i <= 2", "3 > i"]


def test_helper_requires_exactly_one_blank():
    with pytest.raises(AssertionError):
        FB("fundamentals", "beginner", "cpp", "t", "x = 1;", "p", ["1"], [], [], "r")


@pytest.mark.parametrize("answer", ["i < 3", "i<3", "  I < 3 ;", "i <= 2", "3>i", "The blank is `i < 3` because it stops at 3"])
def test_equivalent_answers_are_accepted(answer):
    assert fill_blank_hit(answer, _q()["rubric"]["accepted_answers"])


@pytest.mark.parametrize("answer", ["i <= 3", "i > 3", "i++", "no idea"])
def test_wrong_answers_are_rejected(answer):
    assert fill_blank_hit(answer, _q()["rubric"]["accepted_answers"]) is None


def test_quote_styles_and_semicolons_are_equivalent():
    assert fill_blank_hit("echo 'Hi';", ['echo "Hi"'])
    assert fill_blank_hit('print("done")', ["print('done')"])


def test_short_correct_answer_is_graded_correct():
    fb = grade("i<3", _ctx(_q()))
    assert fb.verdict == "correct" and fb.correctness_score >= 0.8
    assert not any("very short" in g.description for g in fb.reasoning_gaps)


def test_wrong_fill_is_incorrect_and_flags_the_misconception():
    fb = grade("i <= 3", _ctx(_q()))
    assert fb.verdict == "incorrect"
    assert [m.name for m in fb.misconceptions] == ["uses <= 3"]
    assert any("i < 3" in s for s in fb.suggestions)


def test_explain_questions_are_unaffected():
    from app.content.bank import SEED_QUESTIONS

    q = next(x for x in SEED_QUESTIONS if "kind" not in x["rubric"])
    fb = grade(q["rubric"]["reference_answer"], _ctx(q))
    assert fb.verdict == "correct"


def test_identifier_boundaries_are_respected():
    assert fill_blank_hit("background-color: red", ["color: red"]) is None
    assert fill_blank_hit("color:red;", ["color: red"])
    assert fill_blank_hit("i < 30", ["i < 3"]) is None
    assert fill_blank_hit("let", ["let"]) and fill_blank_hit("outlet", ["let"]) is None
    assert fill_blank_hit("int &x", ["int& x"]) and fill_blank_hit("return  a;", ["return a"])
