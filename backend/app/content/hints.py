"""Progressive hints for every question, derived offline from its rubric.

Each question gets exactly three hints, revealed one at a time:
  1. a strategy nudge for the skill (how to attack this kind of question),
  2. the key idea (the "why" points of the rubric),
  3. the point the answer must make (or, for fill-in questions, how the
     missing code starts).
Hints are written into the question's rubric at seed time (``rubric["hints"]``),
so no LLM is called at runtime. A question may define its own ``hints`` list,
which is kept as is.
"""

from __future__ import annotations

HINT_LEVELS = 3

STRATEGY = {
    "fundamentals": "Go one line at a time and write down the value of every variable after each step.",
    "code_tracing": "Trace it like the computer would: keep a small table of each variable and update it line by line.",
    "debugging": "Pick a concrete input, run it in your head, and find the first line that does something the author did not intend.",
    "algorithmic_thinking": "Count how many times the innermost line runs as the input size n grows.",
    "edge_cases_testing": "Try the extremes: empty input, one item, zero, negative numbers, very large values and duplicates.",
    "code_review_design": "Read it as a reviewer: what could break, what is hard to read, and what is risky for security or speed?",
    "data_structures": "Ask which operation happens most often (lookup, insert, ordered walk) and which container makes it cheap.",
    "oop": "Check which class owns the method or attribute, which object self / this / $this points to, and whether state lives on the class or the instance.",
    "algorithms": "Say the approach in one sentence, then why it always gives the right answer, then what it costs.",
    "logic_problems": "Write out the cases (or a small truth table) and check each one before you conclude.",
}
# Markup and pseudocode need a different first nudge than "track the variables".
LANGUAGE_STRATEGY = {
    "html": "Picture how the browser builds the page: which elements exist, how they nest, and what each tag means.",
    "css": "Work out which rules match the element, then which one wins (specificity first, then source order).",
    "general": "Work through it on paper, one step at a time, writing down every value as it changes.",
}
FILL_STRATEGY = (
    "Read the lines around the ? slot. What must be there for the code to do exactly what the prompt "
    "and the comments say?"
)


def _sentence(label: str) -> str:
    # Keep the original casing: labels often start with code (maxOf, range, std::).
    label = label.strip().rstrip(".")
    return label + "." if label else ""


def _code_prefix(code: str) -> str:
    """Show roughly the first third of the missing code (at least one character)."""
    n = max(1, round(len(code) / 3))
    return code[:n]


def build_hints(q: dict) -> list[str]:
    rubric = q.get("rubric") or {}
    if rubric.get("hints"):
        return list(rubric["hints"])[:HINT_LEVELS]
    concepts = rubric.get("concepts") or []
    labels = [c["label"] for c in concepts if c.get("label")]
    primary, secondary = (labels[0] if labels else ""), labels[1:]
    misconceptions = rubric.get("misconceptions") or []

    if rubric.get("kind") == "fill_blank":
        accepted = rubric.get("accepted_answers") or [""]
        first = accepted[0]
        why = " ".join(_sentence(s) for s in secondary[:2]) or "Think about what the surrounding lines need from it."
        return [
            FILL_STRATEGY,
            f"Key idea: {why}",
            f"The missing code starts with “{_code_prefix(first)}…” ({len(first)} characters in one accepted answer).",
        ]

    domain = q.get("domain", "")
    first_hint = STRATEGY.get(domain, STRATEGY["code_tracing"])
    if domain in ("fundamentals", "code_tracing") and q.get("language") in LANGUAGE_STRATEGY:
        first_hint = LANGUAGE_STRATEGY[q["language"]]
    if secondary:
        second = "Key idea: " + " ".join(_sentence(s) for s in secondary[:2])
    elif misconceptions:
        second = "Watch out for a common trap: " + _sentence(misconceptions[0].get("explanation", "") or misconceptions[0]["label"])
    else:
        second = "Key idea: connect what happens to the exact line that causes it, and say why."
    third = "Your answer should make this point: " + _sentence(primary)
    return [first_hint, second, third]


def with_hints(questions: list[dict]) -> list[dict]:
    """Attach hints to every question's rubric (idempotent)."""
    for q in questions:
        q["rubric"]["hints"] = build_hints(q)
    return questions
