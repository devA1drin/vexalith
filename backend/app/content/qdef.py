"""Compact question definition helpers."""

from __future__ import annotations

# Marker for the missing piece in a fill-in-the-missing-code snippet.
BLANK = "____"
FILL_BLANK = "fill_blank"


def Q(domain, difficulty, language, title, code, prompt, concepts, misconceptions, reference):  # noqa: N802
    return {
        "domain": domain,
        "difficulty": difficulty,
        "language": language,
        "title": title,
        "code": code,
        "prompt": prompt,
        "rubric": {
            "concepts": [{"label": c[0], "keywords": list(c[1]), "weight": c[2]} for c in concepts],
            "misconceptions": [{"label": m[0], "keywords": list(m[1]), "explanation": m[2]} for m in misconceptions],
            "reference_answer": reference,
        },
    }


def FB(domain, difficulty, language, title, code, prompt, accepted, concepts, misconceptions, reference):  # noqa: N802
    """Fill-in-the-missing-code question.

    ``code`` contains exactly one ``____`` blank. ``accepted`` lists every answer
    that correctly fills it (matched whitespace-, case- and quote-insensitively,
    with an optional trailing semicolon). The first rubric concept is "fills the
    blank"; ``concepts`` add the reasoning points (why it works).
    """
    assert code.count(BLANK) == 1, title
    assert accepted, title
    q = Q(domain, difficulty, language, title, code, prompt,
          [(f"fills the blank with {accepted[0]}", accepted, 2), *concepts], misconceptions, reference)
    q["rubric"]["kind"] = FILL_BLANK
    q["rubric"]["accepted_answers"] = list(accepted)
    return q
