"""Human-friendly wording for every question, applied when the bank is built.

Learners told us some prompts read like an exam paper ("Quantify.", "What is
logged?"). This module rewrites each prompt in plain words and adds a clear
"Your task" line that says exactly what to do and what a good answer contains.

Only the wording changes: titles (the seed upsert key), code, rubrics, accepted
answers and hints stay the same, so grading and tests keep working. Each
question also gets a short "how to answer" guide in ``rubric["guide"]`` that
the practice page shows before the learner starts typing.
"""

from __future__ import annotations

import re

# Whole sentences that were too terse or exam-like → plain wording.
SENTENCES = {
    "What is printed?": "What does this code print?",
    "What exactly is printed?": "What does it print, exactly?",
    "What is logged?": "What does this code show in the console?",
    "Why?": "Why does that happen?",
    "What, and why?": "What happens, and why?",
    "Explain and fix.": "Explain what goes wrong, then show how to fix it.",
    "Fix it.": "Then show how to fix it.",
    "Fix the check.": "Then show how to fix the check.",
    "Quantify.": "Use numbers to back it up (for example, how many steps or how much memory).",
    "Show the case analysis.": "Check each possible case, one at a time.",
    "Explain why.": "Explain why in your own words.",
    "What happens?": "What happens when this runs?",
    "What comes next?": "What comes next in the pattern?",
}

# Word-level swaps for jargon a beginner may not know.
WORDS = [
    (r"\bPredict\b", "Work out"),
    (r"\bpredict\b", "work out"),
    (r"\bJustify\b", "Explain"),
    (r"\bjustify\b", "explain"),
    (r"\bidiomatic\b", "clean, natural"),
    (r"\bIdiomatic\b", "Clean, natural"),
    (r"\bAsymptotic\b", "Big-O"),
    (r"\basymptotic\b", "Big-O"),
]

GLOSSARY = [
    ("Big-O", "Big-O (how the amount of work grows as the input gets bigger)"),
    ("time complexity", "time complexity (how the running time grows as the input gets bigger)"),
]

# "Your task" line per skill: what to do + what a good answer contains.
TASKS = {
    "fundamentals": "Your task: in 2-4 short sentences, give your answer first, then explain it line by line in plain words.",
    "code_tracing": "Your task: write the exact output (or result) first, then explain in 2-4 sentences why, following the code line by line.",
    "debugging": "Your task: in 2-4 sentences, name the bug, point to the line that causes it, say why it's wrong, and show the fixed code.",
    "algorithmic_thinking": "Your task: give the Big-O, explain how you counted the steps, and say how it could be made faster if you can.",
    "edge_cases_testing": "Your task: list the inputs that break it (empty, zero, negative, huge, duplicates...). For each one, say what goes wrong and how to fix it.",
    "code_review_design": "Your task: name the main problem, explain why it matters (bugs, safety, speed or readability), and say how you would change the code.",
    "data_structures": "Your task: name the structure you'd use, say which operation it makes fast, and compare it with the current choice.",
    "oop": "Your task: in 2-4 sentences, answer the question, then explain which object or class is doing the work and why.",
    "algorithms": "Your task: describe the idea in plain words, explain why it always gives the right answer, and say how fast it is.",
    "logic_problems": "Your task: give your answer, then show the steps or cases that prove it.",
}
MARKUP_TASK = "Your task: in 2-4 sentences, say what the browser shows or does, and which tag, attribute or rule causes it."
FILL_TASK = "Your task: type only the code that goes in the ? slot. If you like, add one short sentence on why it fits."

# What to look for while reading the code (the "How to answer" guide).
LOOK_FOR = {
    "fundamentals": "Read one line at a time and keep track of each variable's value.",
    "code_tracing": "Follow the code like the computer does: loops, conditions and the value of each variable.",
    "debugging": "Try a small example input and find the first line that does something unexpected.",
    "algorithmic_thinking": "Look at the loops: how many times does the innermost line run for n items?",
    "edge_cases_testing": "Think about unusual inputs: nothing at all, one item, zero, negative or very large values.",
    "code_review_design": "Read it like a teammate reviewing a pull request: what could break, leak or confuse?",
    "data_structures": "Spot the operation that happens most (lookup, insert, ordered walk).",
    "oop": "Check which class defines each method and which object self / this / $this points to.",
    "algorithms": "Look for the main idea (two pointers, sorting, a hash map, recursion) and what it costs.",
    "logic_problems": "Write the facts down and test each possibility, one at a time.",
}
MARKUP_LOOK = "Picture the page in the browser: which elements exist and which CSS rule wins."
FILL_LOOK = "Read the lines just before and after the ? slot. What must be there for the code to do its job?"

GOOD_ANSWER = {
    "explain": "A good answer states the result first, then gives the reason. Casual wording is fine, and so are English, Filipino or Taglish.",
    "fill_blank": "A good answer is just the right code, e.g. i += 1. Spacing, quote style and a trailing ; don't matter.",
}


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s]


def plain_prompt(prompt: str) -> str:
    """Rewrite the question part of a prompt in plain words."""
    out = []
    for s in _sentences(prompt):
        s = SENTENCES.get(s, s)
        for pat, rep in WORDS:
            s = re.sub(pat, rep, s)
        out.append(s)
    text = " ".join(out)
    for term, explained in GLOSSARY:
        if term in text and explained not in text:
            text = text.replace(term, explained, 1)
            break
    if text and text[-1] not in ".?!:)":
        text += "."
    return text


def task_line(q: dict) -> str:
    rubric = q.get("rubric") or {}
    if rubric.get("kind") == "fill_blank":
        return FILL_TASK
    domain = q.get("domain", "")
    if q.get("language") in ("html", "css") and domain in ("fundamentals", "code_tracing"):
        return MARKUP_TASK
    return TASKS.get(domain, TASKS["code_tracing"])


def guide(q: dict) -> dict:
    rubric = q.get("rubric") or {}
    kind = "fill_blank" if rubric.get("kind") == "fill_blank" else "explain"
    domain = q.get("domain", "")
    if kind == "fill_blank":
        look = FILL_LOOK
    elif q.get("language") in ("html", "css") and domain in ("fundamentals", "code_tracing"):
        look = MARKUP_LOOK
    else:
        look = LOOK_FOR.get(domain, LOOK_FOR["code_tracing"])
    task = task_line(q).removeprefix("Your task: ")
    return {"task": task[:1].upper() + task[1:], "look_for": look, "good_answer": GOOD_ANSWER[kind]}


def humanize(q: dict) -> dict:
    """Rewrite one question's prompt (idempotent) and attach its guide."""
    rubric = q.setdefault("rubric", {})
    original = rubric.get("original_prompt") or q["prompt"]
    rubric["original_prompt"] = original
    q["prompt"] = plain_prompt(original) + "\n\n" + task_line(q)
    rubric["guide"] = guide(q)
    return q


def with_human_prompts(questions: list[dict]) -> list[dict]:
    for q in questions:
        humanize(q)
    return questions
