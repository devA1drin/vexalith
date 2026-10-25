"""Understand natural, casual human answers.

People don't write like a textbook: they use contractions ("doesn't"), slang
("cuz", "spits out"), number words ("prints five") and make typos ("varible").
This module turns an answer into an extra *canonical view* that the rubric
grader also checks, and provides a small typo-tolerant word match.

Nothing here can make a wrong idea right: it only maps everyday wording onto
the words the rubric already uses. Misconception checks stay strict.
"""

from __future__ import annotations

import re

CONTRACTIONS = {
    "can't": "cannot", "cant": "cannot", "won't": "will not", "wont": "will not",
    "n't": " not", "'re": " are", "'s": " is", "'ll": " will", "'ve": " have", "'d": " would", "'m": " am",
}

# Casual / everyday phrase → the words a textbook answer would use (appended, never replaced).
CASUAL = [
    (r"\b(spits? out|shows? up|outputs|displays|echoes|prints? out)\b", "prints", "output"),
    (r"\b(gives? back|hands? back|spits? back|comes? back with)\b", "returns", ""),
    (r"\b(never (ends|stops|finishes)|goes on forever|runs forever|keeps? (going|running|looping) forever|loops? forever|forever loop|endless loop|stuck in (a|the) loop)\b", "infinite loop", "never terminates"),
    (r"\b(blows? up|crash(es|ed)?|errors? out|throws? an error|bombs?)\b", "throws an error", "exception crash"),
    (r"\b(same (thing|box|spot|place) in memory|points? (to|at) the same|both point)\b", "same object", "reference"),
    (r"\b(gets? bigger|goes? up|bumps? up)\b", "increases", "increments"),
    (r"\b(gets? smaller|goes? down)\b", "decreases", "decrements"),
    (r"\b(jumps? over|skips? over)\b", "skips", ""),
    (r"\b(two times|2 times|2x)\b", "twice", ""),
    (r"\b(gets? lost|disappears?|is gone|vanish(es)?)\b", "lost", ""),
    (r"\b(glue[sd]? together|sticks? together)\b", "concatenates", "concatenation"),
    (r"\b(gets slower as the list grows|gets slower)\b", "slower", "complexity grows"),
]

SLANG = {
    "cuz": "because", "coz": "because", "cos": "because", "cause": "because", "bc": "because", "b/c": "because",
    "bcs": "because", "becuz": "because", "becoz": "because", "u": "you", "ur": "your", "thru": "through",
    "gonna": "going to", "wanna": "want to", "gotta": "has to", "kinda": "kind of", "w/": "with", "w/o": "without",
    "n": "and", "yep": "yes", "yeah": "yes", "nope": "no", "tho": "though", "pls": "please", "prolly": "probably",
    "func": "function", "var": "variable", "obj": "object", "arr": "array", "str": "string", "num": "number",
}

NUMBERS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "twenty": "20", "hundred": "100",
}

_WORD = re.compile(r"[a-z0-9_/']+")


def canonical(text: str, *, extras: bool = True) -> str:
    """Return an English view of a casual answer (contractions expanded, slang and number words mapped)."""
    t = text.lower().replace("\u2019", "'").replace("\u2018", "'")
    t = re.sub(r"\b(can't|cant|won't|wont)\b", lambda m: CONTRACTIONS[m.group(1)], t)
    t = re.sub(r"(\w)(n't)\b", r"\1 not", t)
    # Contractions typed without the apostrophe ("didnt", "doesnt", "isnt").
    t = re.sub(r"\b(did|does|do|is|was|are|were|has|have|had|could|should|would)nt\b", r"\1 not", t)
    t = re.sub(r"(\w)('re|'ll|'ve|'d|'m)\b", lambda m: m.group(1) + CONTRACTIONS[m.group(2)], t)
    t = re.sub(r"\b(it|that|there|what|he|she|who|here)'s\b", r"\1 is", t)
    words = []
    for tok in re.split(r"(\s+)", t):
        core = tok.strip(".,!?;:()\"")
        if core in SLANG:
            tok = tok.replace(core, SLANG[core])
        elif core in NUMBERS:
            tok = tok.replace(core, NUMBERS[core])
        words.append(tok)
    t = "".join(words)
    extra = []
    for pat, primary, more in CASUAL:
        if re.search(pat, t):
            t = re.sub(pat, primary, t)
            if more:
                extra.append(more)
    if not extras:
        return t
    return t + (" " + " ".join(extra) if extra else "")


def _edits_within(a: str, b: str, limit: int) -> bool:
    """True when the edit distance (with swapped letters as one edit) between a and b is <= limit (banded, early exit)."""
    if abs(len(a) - len(b)) > limit:
        return False
    prev = list(range(len(b) + 1))
    prev2 = prev
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        best = cur[0]
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
            if i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                cur[j] = min(cur[j], prev2[j - 2] + 1)  # swapped neighbours ("teh") count as one typo
            best = min(best, cur[j])
        if best > limit:
            return False
        prev2, prev = prev, cur
    return prev[-1] <= limit


def _allowed(word: str) -> int:
    return 0 if len(word) < 5 else (1 if len(word) < 9 else 2)


def _word_close(token: str, kw: str) -> bool:
    if token == kw or token.startswith(kw):
        return True
    limit = _allowed(kw)
    if not limit or token[:1] != kw[:1]:
        return False
    # Keywords are often stems ("mutat", "immutab"): compare against the token's prefix too.
    if _edits_within(token, kw, limit):
        return True
    # Short stems ("const") must not fuzzy-match the start of unrelated long words ("consectetur").
    return len(kw) >= 7 and len(token) > len(kw) and _edits_within(token[: len(kw)], kw, limit)


def fuzzy_hit(tokens: list[str], keyword: str) -> bool:
    """Typo-tolerant match of an alphabetic keyword (one or more words) against answer tokens."""
    kws = _WORD.findall(keyword.lower())
    if not kws or " ".join(kws) != " ".join(keyword.lower().split()):
        return False  # symbols / code (e.g. "[1, 9]", "o(n)") must match exactly
    if not any(w.isalpha() and len(w) >= 5 for w in kws):
        return False
    n = len(kws)

    def ok(tok: str, kw: str) -> bool:
        return _word_close(tok, kw) if kw.isalpha() and len(kw) >= 5 else tok == kw

    for i in range(len(tokens) - n + 1):
        if all(ok(tokens[i + j], kws[j]) for j in range(n)):
            return True
    return False


def tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())
