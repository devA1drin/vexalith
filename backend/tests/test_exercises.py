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
        assert e["topic"] and e["task"].startswith("Your task: ")
        json.dumps([t["args"] for t in e["tests"]])
    assert set(COMING_SOON_LANGUAGES) == {"cpp", "java", "php"}


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
    assert body["coming_soon"] == ["cpp", "java", "php"]
    assert len(body["exercises"]) == len(EXERCISES)
    d = client.get("/api/exercises/py-fizzbuzz", headers=H).json()
    assert d["visible_tests"][0]["expected"] == ["1", "2", "Fizz", "4", "Buzz"]
    assert d["hidden_tests"] and all(set(t) == {"args"} for t in d["hidden_tests"])
    assert d["task"].startswith("Your task: ") and d["topic"] == "Loops & conditions"
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
