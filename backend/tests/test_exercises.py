"""Browser coding exercises: content is valid, solutions pass, the server only compares outputs."""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from app.content.exercises import COMING_SOON_LANGUAGES, EXERCISES, RUNNABLE_LANGUAGES
from tests.conftest import auth

H = auth(pid="7001", name="Coder", email="coder@example.com")


def _run_python(code: str, fn: str, args: list):
    ns: dict = {}
    exec(code, ns)  # trusted reference solutions from our own content file, test-only
    return json.loads(json.dumps(ns[fn](*args)))


def test_exercise_content_is_well_formed():
    slugs = [e["slug"] for e in EXERCISES]
    assert len(slugs) == len(set(slugs)) >= 24
    for e in EXERCISES:
        assert e["language"] in RUNNABLE_LANGUAGES
        assert e["difficulty"] in ("beginner", "intermediate", "advanced")
        assert e["function"] in e["starter"] and e["function"] in e["solution"]
        assert 1 <= e["visible"] < len(e["tests"]), e["slug"]  # at least one hidden test
        assert 1000 <= e["timeout_ms"] <= 10000
        assert e["topic"]
        json.dumps([t["args"] for t in e["tests"]])
    assert COMING_SOON_LANGUAGES == ()
    counts = {lang: sum(e["language"] == lang for e in EXERCISES) for lang in RUNNABLE_LANGUAGES}
    assert min(counts.values()) >= 10, counts


TYPES = {"int", "long", "bool", "str", "int[]", "str[]", "map"}


@pytest.mark.parametrize("e", [e for e in EXERCISES if e["language"] in ("cpp", "java", "php")], ids=lambda e: e["slug"])
def test_typed_exercises_have_a_signature_matching_their_tests(e):
    sig = e["signature"]
    assert set(sig["params"]) <= TYPES and sig["returns"] in TYPES
    for t in e["tests"]:
        assert len(t["args"]) == len(sig["params"])
        for a, ty in zip(t["args"], sig["params"]):
            ok = {"int": lambda v: type(v) is int, "str": lambda v: isinstance(v, str),
                  "int[]": lambda v: isinstance(v, list) and all(type(x) is int for x in v)}[ty](a)
            assert ok, (e["slug"], a, ty)
    if e["language"] == "java":
        assert "class Solution" in e["starter"] and "class Solution" in e["solution"]
    if e["language"] == "php":
        assert e["starter"].startswith("<?php") and e["solution"].startswith("<?php")


@pytest.mark.parametrize("e", [e for e in EXERCISES if e["language"] == "python"], ids=lambda e: e["slug"])
def test_python_reference_solutions_pass_and_starters_fail(e):
    for t in e["tests"]:
        assert _run_python(e["solution"], e["function"], t["args"]) == t["expected"], e["slug"]
    starter_ok = all(_run_python(e["starter"], e["function"], t["args"]) == t["expected"] for t in e["tests"])
    assert not starter_ok, "starter code must not already solve the exercise"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_javascript_reference_solutions_pass():
    for e in [e for e in EXERCISES if e["language"] == "javascript"]:
        script = e["solution"] + f"\nconst tests = {json.dumps(e['tests'])};\n" + (
            f"console.log(JSON.stringify(tests.map(t => JSON.stringify({e['function']}(...t.args)))));"
        )
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=20, check=True).stdout
        got = [json.loads(x) for x in json.loads(out)]
        assert got == [t["expected"] for t in e["tests"]], e["slug"]


def test_list_and_detail_never_leak_hidden_expected_values(client):
    r = client.get("/api/exercises", headers=H)
    assert r.status_code == 200
    body = r.json()
    assert body["coming_soon"] == []
    assert len(body["exercises"]) == len(EXERCISES)
    d = client.get("/api/exercises/py-fizzbuzz", headers=H).json()
    assert d["visible_tests"][0]["expected"] == ["1", "2", "Fizz", "4", "Buzz"]
    assert d["hidden_tests"] and all(set(t) == {"args"} for t in d["hidden_tests"])
    assert d["topic"] == "Loops & conditions"
    assert client.get("/api/exercises/nope", headers=H).status_code == 404
    assert client.get("/api/exercises").status_code == 401


def _results(e, outputs):
    return [{"output": json.dumps(o)} for o in outputs]


def test_submit_compares_outputs_and_records_solve(client):
    e = next(x for x in EXERCISES if x["slug"] == "py-sum-list")
    wrong = [0] * len(e["tests"])
    r = client.post("/api/exercises/py-sum-list/submit", headers=H, json={"code": "def total(n): return 0", "results": _results(e, wrong)})
    j = r.json()
    assert r.status_code == 200 and not j["solved"] and j["passed"] < j["total"]
    assert all("expected" not in c for c in j["checks"] if not c["visible"])
    right = [t["expected"] for t in e["tests"]]
    j = client.post("/api/exercises/py-sum-list/submit", headers=H, json={"code": e["solution"], "results": _results(e, right)}).json()
    assert j["solved"] and j["first_solve"] and j["passed"] == j["total"]
    j = client.post("/api/exercises/py-sum-list/submit", headers=H, json={"code": e["solution"], "results": _results(e, right)}).json()
    assert j["solved"] and not j["first_solve"]
    listing = {x["slug"]: x for x in client.get("/api/exercises?language=python", headers=H).json()["exercises"]}
    assert listing["py-sum-list"]["solved"] and all(x["language"] == "python" for x in listing.values())


def test_submit_rejects_wrong_shape_and_counts_errors_as_failures(client):
    e = next(x for x in EXERCISES if x["slug"] == "js-reverse-string")
    assert client.post("/api/exercises/js-reverse-string/submit", headers=H, json={"code": "x", "results": []}).status_code == 422
    res = [{"output": None, "error": "Timed out after 4s"}] + [{"output": json.dumps(t["expected"])} for t in e["tests"][1:]]
    j = client.post("/api/exercises/js-reverse-string/submit", headers=H, json={"code": "x", "results": res}).json()
    assert j["passed"] == len(e["tests"]) - 1 and not j["checks"][0]["passed"]
    # Outputs that aren't JSON are just wrong, never a server error.
    res = [{"output": "not json"} for _ in e["tests"]]
    assert client.post("/api/exercises/js-reverse-string/submit", headers=H, json={"code": "x", "results": res}).json()["passed"] == 0


def test_canonical_treats_whole_floats_as_ints_but_keeps_real_fractions():
    from app.api.exercises import canonical

    assert canonical([3.0, {"b": 2.0, "a": [1.0]}]) == canonical([3, {"a": [1], "b": 2}])
    assert canonical(2.5) != canonical(2)
    assert canonical(True) == "true"


def test_submit_for_a_typed_language_accepts_whole_floats(client):
    e = next(x for x in EXERCISES if x["slug"] == "php-sum-list")
    res = [{"output": json.dumps(float(t["expected"]))} for t in e["tests"]]
    j = client.post("/api/exercises/php-sum-list/submit", headers=H, json={"code": e["solution"], "results": res}).json()
    assert j["solved"] and j["message"] == "All tests passed. Nice work!"


# ---- "How to solve it": hints, generalized explanation, solution reveal ----

from app.content.exercise_guides import GUIDES, commented_solution, concept_of, explanation_for, hints_for  # noqa: E402


@pytest.mark.parametrize("e", EXERCISES, ids=lambda e: e["slug"])
def test_every_exercise_has_progressive_hints_and_a_generalized_explanation(e):
    assert concept_of(e["slug"]) in GUIDES
    hints = hints_for(e["slug"], e["language"])
    assert 2 <= len(hints) <= 3 and len(set(hints)) == len(hints)
    x = explanation_for(e["slug"], e["language"])
    assert x["idea"] and x["pattern"] and 3 <= len(x["approach"]) <= 5 and 2 <= len(x["pitfalls"]) <= 4
    text = " ".join([*hints, x["idea"], x["pattern"], *x["approach"], *x["pitfalls"]])
    assert "{" not in text and "}" not in text  # every language placeholder was filled in
    assert "line " not in text.lower()  # general strategy, not a line-by-line walkthrough
    sol = commented_solution(e["slug"], e["language"], e["solution"])
    assert sol.endswith(e["solution"].removeprefix("<?php\n")) and len(sol.splitlines()) == len(e["solution"].splitlines()) + 1


@pytest.mark.parametrize("e", [e for e in EXERCISES if e["language"] == "python"], ids=lambda e: e["slug"])
def test_commented_python_solutions_still_pass(e):
    sol = commented_solution(e["slug"], "python", e["solution"])
    for t in e["tests"]:
        assert _run_python(sol, e["function"], t["args"]) == t["expected"]


def test_help_is_hidden_until_earned_and_hints_reveal_one_at_a_time(client):
    h = auth(pid="7101", name="Helper", email="helper@example.com")
    d = client.get("/api/exercises/py-two-sum", headers=h).json()
    assert d["help"] == {"hint_count": 3, "hints": [], "solution_revealed": False, "solved_with_help": False, "explanation": None, "solution": None}
    assert "seen" not in json.dumps(d["help"])  # nothing of the reference solution leaks
    one = client.post("/api/exercises/py-two-sum/hints", headers=h).json()
    assert len(one["hints"]) == 1 and one["solution"] is None and one["explanation"] is None
    for _ in range(4):
        last = client.post("/api/exercises/py-two-sum/hints", headers=h).json()
    assert len(last["hints"]) == 3  # capped
    assert client.get("/api/exercises/py-two-sum", headers=h).json()["help"]["hints"] == last["hints"]
    assert client.post("/api/exercises/nope/hints", headers=h).status_code == 404
    assert client.post("/api/exercises/py-two-sum/hints").status_code == 401


def test_solution_needs_an_attempt_or_a_confirm_and_marks_solved_with_help(client):
    h = auth(pid="7102", name="Peeker", email="peeker@example.com")
    assert client.post("/api/exercises/py-sum-list/solution", headers=h, json={}).status_code == 409
    j = client.post("/api/exercises/py-sum-list/solution", headers=h, json={"confirm": True}).json()
    assert j["solution_revealed"] and j["solved_with_help"] and "for n in nums" in j["solution"]
    assert j["explanation"]["idea"] and j["explanation"]["approach"]
    e = next(x for x in EXERCISES if x["slug"] == "py-sum-list")
    right = [_run_python(e["solution"], "total", t["args"]) for t in e["tests"]]
    client.post("/api/exercises/py-sum-list/submit", headers=h, json={"code": e["solution"], "results": _results(e, right)})
    listing = {x["slug"]: x for x in client.get("/api/exercises?language=python", headers=h).json()["exercises"]}
    assert listing["py-sum-list"]["solved"] and listing["py-sum-list"]["solved_with_help"]

    # After a failed submit no confirm is needed.
    e2 = next(x for x in EXERCISES if x["slug"] == "py-largest")
    client.post("/api/exercises/py-largest/submit", headers=h, json={"code": "x", "results": [{"output": "0"} for _ in e2["tests"]]})
    assert client.post("/api/exercises/py-largest/solution", headers=h, json={}).status_code == 200


def test_passing_unlocks_the_explanation_without_marking_help(client):
    h = auth(pid="7103", name="Solver", email="solver@example.com")
    e = next(x for x in EXERCISES if x["slug"] == "py-reverse-string")
    right = [_run_python(e["solution"], "reverse", t["args"]) for t in e["tests"]]
    j = client.post("/api/exercises/py-reverse-string/submit", headers=h, json={"code": e["solution"], "results": _results(e, right)}).json()
    assert j["solved"] and j["help"]["explanation"]["pattern"] and j["help"]["solution"]
    assert not j["help"]["solved_with_help"]
    wrong = client.post("/api/exercises/py-fizzbuzz/submit", headers=h, json={"code": "x", "results": [{"output": "0"}] * 4}).json()
    assert wrong["help"]["solution"] is None and wrong["help"]["explanation"] is None
    listing = {x["slug"]: x for x in client.get("/api/exercises?language=python", headers=h).json()["exercises"]}
    assert listing["py-reverse-string"]["solved"] and not listing["py-reverse-string"]["solved_with_help"]
