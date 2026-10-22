"""Compact question definition helper."""

from __future__ import annotations


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
