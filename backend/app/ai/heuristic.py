"""
Offline rubric-based grader for programming explanations.

Each seeded question stores a rubric:
  concepts:       [{label, keywords[], weight}]  ideas a correct answer contains
  misconceptions: [{label, keywords[], explanation}]
  reference_answer: str

Scoring (explainable):
  correctness = weighted share of rubric concepts mentioned (keyword/concept match)
  reasoning   = explanation quality: length + causal/technical reasoning markers
  overall     = 0.7 * correctness + 0.3 * reasoning − 0.12 per misconception
A misconception only counts when the primary concept was NOT hit, so an answer
that says "with let it would print 0 1 2" is not punished for mentioning it.
"""

from __future__ import annotations

import re

from app.ai.casual import canonical, fuzzy_hit, tokens
from app.ai.filipino import gloss as filipino_gloss
from app.ai.provider import AIProvider, QuestionContext
from app.schemas.schemas import FeedbackPayload, Finding, ReasoningGap

_MARKER_WORDS = (
    r"because|since|therefore|so that|so the|which means|this means|thus|hence|as a result|"
    r"instead|however|whereas|otherwise|if|when|until|each|every|iteration|loop|complexity|"
    r"o\(|edge case|invariant|fix|should|returns?|throws?|raises?"
)
REASONING_MARKERS = re.compile(r"\b(" + _MARKER_WORDS + r")\b", re.I)
# On the English gloss of a Filipino answer, "kaya" ("so the result ...") becomes a bare
# "so": count it as a connective there.
GLOSS_MARKERS = re.compile(r"\b(" + _MARKER_WORDS + r"|so)\b", re.I)
_WS = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WS.sub(" ", text.lower()).strip()


def _despace(text: str) -> str:
    return _WS.sub("", text.lower())


def keyword_hit(answer_norm: str, answer_compact: str, keyword: str) -> bool:
    """Match a rubric keyword against the answer.

    Alphanumeric keywords match at a word start (so stems like 'mutat' work and
    '6' doesn't match '16'); keywords with symbols (e.g. '[1, 9]') also match
    with whitespace removed on both sides.
    """
    kw = keyword.lower().strip()
    if not kw:
        return False
    if re.fullmatch(r"[a-z0-9_ .'-]+", kw) and kw[0].isalnum():
        return re.search(r"(?<![a-z0-9])" + re.escape(kw), answer_norm) is not None
    return kw in answer_norm or _despace(kw) in answer_compact


_QUOTES = str.maketrans({"'": '"', "`": '"', "\u2018": '"', "\u2019": '"', "\u201c": '"', "\u201d": '"'})


def _code_norm(text: str) -> str:
    """Normalise code for blank matching.

    Lower case, one quote style, single spaces only between word characters
    (so "i < 3" == "i<3" but "return a" keeps its word boundary), no trailing ;.
    """
    t = _WS.sub(" ", text.lower().translate(_QUOTES)).strip()
    t = re.sub(r"\s*([^\w\s])\s*", r"\1", t)
    return t.rstrip(";")


def _contains_code(haystack: str, needle: str) -> bool:
    """Substring match that respects identifier boundaries ("color" is not in "background-color")."""
    if not needle:
        return False
    pat = re.escape(needle)
    if re.match(r"\w", needle):
        pat = r"(?<![\w-])" + pat
    if re.search(r"\w$", needle):
        pat += r"(?!\w)"
    return re.search(pat, haystack) is not None


def fill_blank_hit(answer: str, accepted: list[str]) -> str | None:
    """Return the accepted answer the learner supplied (equivalent forms allowed), if any."""
    norm = _code_norm(answer)
    loose = norm.replace(";", "")  # "i++;" vs "i++", "{return a>b;}" vs "{return a>b}"
    for acc in accepted:
        a = _code_norm(acc)
        if _contains_code(norm, a) or _contains_code(loose, a.replace(";", "")):
            return acc
    return None


def tutor_summary(verdict: str, hit: int, total: int, mixup: bool, fill_blank: bool) -> str:
    """A short, warm summary in the voice of a human tutor (no scoring jargon)."""
    points = f"You got {hit} of the {total} key points." if total else ""
    if verdict == "correct":
        head = "Nice work, that's right!" if not fill_blank else "Yes, that code fits the blank!"
        tail = "Have a quick look at the model answer to see if there's anything you'd add."
    elif verdict == "partially_correct":
        head = "You're on the right track."
        tail = "The unticked points above are what's still missing."
    else:
        head = "Not quite yet, but that's how learning works."
        tail = "Check the model answer below, then give the next one a go."
    if mixup:
        tail = "It looks like you hit a common mix-up, so I explained it below. " + tail
    return " ".join(x for x in (head, points, tail) if x)


def grade(answer: str, question: QuestionContext) -> FeedbackPayload:
    rubric = question.rubric or {}
    concepts = rubric.get("concepts") or []
    misconceptions_r = rubric.get("misconceptions") or []
    reference = rubric.get("reference_answer")

    norm = _normalize(answer)
    compact = _despace(answer)
    # Filipino / Taglish answers are matched through an English gloss as well,
    # so the same ideas score the same in either language.
    g = filipino_gloss(answer)
    views = [(norm, compact)]
    if g.language != "en":
        views += [(_normalize(g.primary), _despace(g.primary)), (_normalize(g.full), _despace(g.full))]
    strict_views = views[:2]
    # Casual human wording ("doesn't", "cuz", "spits out five") is matched through a
    # canonical English view, and small typos ("varible") through a fuzzy word match.
    # Misconceptions are still only checked on what the learner literally wrote.
    casual_texts = [canonical(answer)] + ([canonical(g.full)] if g.language != "en" else [])
    views += [(_normalize(t), _despace(t)) for t in casual_texts]
    token_views = [tokens(answer)] + [tokens(t) for t in casual_texts]

    def said(keyword: str, *, strict: bool = False) -> bool:
        if strict:
            return any(keyword_hit(n, c, keyword) for n, c in strict_views)
        if any(keyword_hit(n, c, keyword) for n, c in views):
            return True
        return any(fuzzy_hit(t, keyword) for t in token_views)

    hit_labels: list[str] = []
    missed_labels: list[str] = []
    total_w = 0.0
    got_w = 0.0
    primary_hit = False
    fill_blank = rubric.get("kind") == "fill_blank"
    accepted = rubric.get("accepted_answers") or []
    blank_hit = fill_blank_hit(answer, accepted) if fill_blank else None
    for i, c in enumerate(concepts):
        w = float(c.get("weight", 1))
        total_w += w
        hit = any(said(k) for k in c.get("keywords", []))
        if fill_blank and i == 0:
            hit = blank_hit is not None
        if hit:
            got_w += w
            hit_labels.append(c["label"])
            if i == 0:
                primary_hit = True
        else:
            missed_labels.append(c["label"])
    correctness = (got_w / total_w) if total_w else 0.5
    if blank_hit is not None:
        # The right code in the blank is a correct answer; the "why" points only add on top.
        correctness = max(correctness, 0.8)

    findings: list[Finding] = []
    if not primary_hit:
        for m in misconceptions_r:
            for k in m.get("keywords", []):
                if said(k, strict=True):
                    findings.append(
                        Finding(name=m["label"], explanation=m["explanation"], evidence_span=k, confidence=0.6)
                    )
                    break

    words = len(answer.split())
    marker_text = canonical(answer, extras=False)
    if g.language != "en":
        # Tagalog needs extra grammar words ("ang", "ng", "mga"); count the gloss
        # words (plus ~30% for the English articles a translation would add) so length is judged fairly.
        gloss_words = sum(1 for t in g.primary.split() if any(ch.isalnum() for ch in t))
        words = min(words, round(gloss_words * 1.3))
        marker_text = canonical(g.primary, extras=False)
    length_score = min(1.0, words / 60.0)
    markers = len((GLOSS_MARKERS if g.language != "en" else REASONING_MARKERS).findall(marker_text))
    marker_score = min(1.0, markers / 5.0)
    reasoning = round(0.5 * length_score + 0.5 * marker_score, 3)

    overall = 0.7 * correctness + 0.3 * reasoning - 0.12 * len(findings)
    overall = round(max(0.0, min(1.0, overall)), 3)
    correctness = round(correctness, 3)

    if correctness >= 0.75 and not findings:
        verdict = "correct"
    elif correctness >= 0.35:
        verdict = "partially_correct"
    else:
        verdict = "incorrect"

    gaps: list[ReasoningGap] = []
    if fill_blank:
        # The answer is code, so don't nag about prose length or "because" markers.
        if blank_hit is None:
            gaps.append(ReasoningGap(
                description="Not quite: the code you typed doesn't fit the blank yet.",
                how_to_improve="Read the lines just before and after the ? slot and ask yourself what has to be there for the code to work.",
            ))
        # Missed points are already unticked in the "full answer covers" checklist.
    else:
        if words < 20:
            gaps.append(ReasoningGap(
                description="Your answer is a bit short, so I can't see all of your thinking yet.",
                how_to_improve="Say your answer first, then walk me through it: what happens on each line that matters?",
            ))
        if marker_score < 0.4:
            gaps.append(ReasoningGap(
                description="You told me what happens, but not much about why.",
                how_to_improve="Link it to the code with a 'because', like: 'it prints 3 because line 2 adds 1 each time'.",
            ))

    suggestions: list[str] = []
    if findings:
        suggestions.append("This is a really common mix-up, so don't worry. Go through the code again one line at a time and you'll spot it.")
    if fill_blank:
        if blank_hit is None and accepted:
            suggestions.append(
                "Look at the lines around the blank and think about what they need from it. "
                "Here's one answer that works: " + accepted[0]
            )
        else:
            suggestions.append("Nice, that code fits! If you want the full score, add one sentence on why it works.")
    elif question.domain_slug == "fundamentals":
        suggestions.append(
            "Tip: say what each line does in plain words and jot down each variable's value as you go. "
            "Then compare with the model answer below."
        )
    elif question.domain_slug == "algorithmic_thinking":
        suggestions.append("To back up your Big-O, count how many times the busiest line runs as the input grows.")
    elif question.domain_slug == "edge_cases_testing":
        suggestions.append("For each tricky input, say what you'd expect, what actually happens, and how to fix it.")
    elif question.domain_slug == "debugging":
        suggestions.append("Point to the line that causes the bug, give an input that shows it, then share the fixed code.")
    elif question.domain_slug == "oop":
        suggestions.append(
            "Ask yourself: which object is self / this / $this right now, which class has this method, and does the value belong to the class or to one object?"
        )
    if not suggestions:
        suggestions.append("Great work! For an extra challenge, think of another way to solve it and what you'd gain or lose.")

    explanation = tutor_summary(verdict, len(hit_labels), len(concepts), bool(findings), fill_blank)
    return FeedbackPayload(
        verdict=verdict,
        correctness_score=correctness,
        reasoning_score=reasoning,
        overall_score=overall,
        strengths=[f"You explained: {h}" for h in hit_labels],
        missed_concepts=missed_labels,
        misconceptions=findings,
        reasoning_gaps=gaps[:4],
        suggestions=suggestions[:4],
        domain_scores={question.domain_slug: overall},
        reference_answer=reference,
        raw_explanation=explanation,
        provider_used="heuristic",
        answer_language=g.language,
    )


class HeuristicProvider(AIProvider):
    name = "heuristic"

    def evaluate_response(self, *, question: QuestionContext, answer: str) -> FeedbackPayload:
        return grade(answer, question)
