"""Filipino / Tagalog / Taglish answers are graded on their ideas, like English ones."""

import pytest

from app.ai.filipino import FILIPINO_NOTE, TAGLISH_NOTE, detect_language, gloss, lemma
from app.ai.heuristic import grade
from app.ai.provider import QuestionContext
from app.content.bank import SEED_QUESTIONS
from app.db.session import SessionLocal
from app.models.models import Question
from tests.conftest import auth

CASES = {
 "Copying a value": {
  "en": "It prints 5. When y = x runs, y gets a copy of the value 5. Changing x to 10 later does not change y, because y has its own value, so y is still 5.",
  "fil": "Ang lalabas ay 5. Nang patakbuhin ang y = x, nakakuha ang y ng kopya ng halaga na 5. Kapag binago ang x sa 10 pagkatapos, hindi nagbabago ang y dahil may sarili itong halaga, kaya 5 pa rin ang y.",
  "taglish": "Mag-print siya ng 5. Noong nag-run ang y = x, nakakuha si y ng copy ng value na 5. Kahit i-change natin ang x to 10, hindi nagbabago ang y kasi may sarili siyang value, so 5 pa rin.",
 },
 "Mutable default argument": {
  "en": "The first call prints [1] and the second call prints [1, 2]. The default list is created once, when the function is defined, so every call shares the same list and append keeps adding to it.",
  "fil": "Ang unang tawag ay maglalabas ng [1] at ang pangalawang tawag ay [1, 2]. Ang default na listahan ay ginawa nang isang beses lang, noong dineklara ang function, kaya iisang listahan ang ginagamit ng bawat tawag at patuloy na nadadagdagan ito ng append.",
  "taglish": "Yung first call ay magpi-print ng [1], tapos yung second call ay [1, 2]. Ang default list ay ginawa isang beses lang noong na-define ang function, kaya parehong listahan ang shared ng lahat ng calls at nag-a-append lang ito.",
 },
 "Leaking a file handle": {
  "en": "If the debug key is missing, the ValueError is raised before f.close() runs, so the file is never closed and the handle leaks. Fix: use a with open(path) as f: block, a context manager that closes the file even when an exception happens.",
  "fil": "Kapag walang debug na key, ang ValueError ay nire-raise bago tumakbo ang f.close(), kaya hindi naisara ang file at tumatagas ang handle. Ayusin: gamitin ang with open(path) as f: na block, isang context manager na nagsasara ng file kahit may exception.",
  "taglish": "Pag missing yung debug key, nagre-raise ng ValueError bago ma-run ang f.close(), kaya hindi naisara ang file at may leak. Ang fix ay gumamit ng with open(path) as f:, context manager siya kaya sasarado ang file kahit may exception.",
 },
 "Sum that stops one short": {
  "en": "The condition i < 5 stops the loop before adding 5, so the total is 1 + 2 + 3 + 4 = 10. It is an off-by-one bug. Fix it with while i <= 5 so the last number is included.",
  "fil": "Ang kondisyon na i < 5 ay humihinto bago idagdag ang 5, kaya ang kabuuan ay 1 + 2 + 3 + 4 = 10. Ito ay off-by-one na bug. Ayusin gamit ang while i <= 5 para kasama ang huling numero.",
  "taglish": "Yung condition na i < 5 ay nag-stop bago ma-add ang 5, kaya ang total ay 1 + 2 + 3 + 4 = 10. Off-by-one bug ito. I-fix gamit ang while i <= 5 para included ang last number.",
 },
 "continue in a while loop": {
  "en": "It prints 1245. When i is 3, continue skips the print and jumps back to the condition. It is not an infinite loop because i++ happens before the continue, so i still grows and the loop ends.",
  "fil": "Ang lalabas ay 1245. Kapag ang i ay 3, nilalaktawan ng continue ang print at bumabalik sa kondisyon. Hindi ito walang katapusan dahil nangyayari muna ang i++ bago ang continue, kaya lumalaki pa rin ang i at natatapos ang loop.",
  "taglish": "Ang output ay 1245. Pag 3 na ang i, ini-skip ng continue ang print tapos babalik sa condition. Hindi siya infinite loop kasi nauuna ang i++ bago ang continue, kaya lumalaki pa rin ang i at matatapos ang loop.",
 },
 "Whole-number division": {
  "en": "It prints 3 1 3.5. 7 / 2 with two ints is integer division, so the decimal part is thrown away and we get 3. 7 % 2 gives the remainder 1. 7.0 is a double, so 7.0 / 2 keeps the decimals: 3.5.",
  "fil": "Ang lalabas ay 3 1 3.5. Ang 7 / 2 na parehong int ay integer division, kaya itinatapon ang desimal at 3 ang resulta. Ang 7 % 2 ay nagbibigay ng natitira na 1. Ang 7.0 ay double, kaya ang 7.0 / 2 ay may desimal: 3.5.",
  "taglish": "Mag-print siya ng 3 1 3.5. Yung 7 / 2 ay int at int kaya integer division, tinatapon ang decimal part so 3. Ang 7 % 2 ay remainder na 1. Double ang 7.0 kaya ang 7.0 / 2 ay may decimals: 3.5.",
 },
}

NONSENSE = [
    "Hindi ko alam, basta gumagana siya.",
    "Ewan ko po, basta ganun talaga yan kasi ganun.",
    "Ang galing ng code, sana all. Salamat po!",
    "Kain tayo mamaya, gutom na ako eh.",
]


def _ctx(title: str) -> QuestionContext:
    q = next(x for x in SEED_QUESTIONS if x["title"] == title)
    return QuestionContext(
        title=title, language=q["language"], code=q["code"], prompt=q["prompt"],
        domain_slug=q["domain"], difficulty=q["difficulty"], rubric=q["rubric"],
    )


@pytest.mark.parametrize("title", list(CASES))
def test_filipino_and_taglish_score_like_english(title):
    ctx = _ctx(title)
    en = grade(CASES[title]["en"], ctx)
    assert en.answer_language == "en" and en.verdict == "correct"
    for kind in ("fil", "taglish"):
        fb = grade(CASES[title][kind], ctx)
        assert fb.answer_language in ("fil", "taglish"), kind
        assert fb.verdict == en.verdict, (kind, fb.missed_concepts)
        assert fb.correctness_score == en.correctness_score, (kind, fb.missed_concepts)
        assert abs(fb.overall_score - en.overall_score) <= 0.1, (kind, fb.overall_score, en.overall_score)


@pytest.mark.parametrize("title", list(CASES))
def test_nonsense_filipino_does_not_score_high(title):
    ctx = _ctx(title)
    for text in NONSENSE:
        fb = grade(text, ctx)
        assert fb.overall_score < 0.3 and fb.verdict == "incorrect", (text, fb.overall_score)


def test_partial_filipino_answer_is_partial():
    # Right output, no reason: same partial result as the English equivalent.
    ctx = _ctx("Copying a value")
    fil = grade("Ang lalabas ay 5.", ctx)
    en = grade("It prints 5.", ctx)
    assert fil.correctness_score == en.correctness_score < 1
    assert fil.verdict == en.verdict == "partially_correct"


def test_misconception_in_filipino_is_detected():
    fb = grade("Ang lalabas ay 10 kasi sinusundan ng y ang x kapag nagbago ito.", _ctx("Copying a value"))
    assert fb.misconceptions and fb.misconceptions[0].name == "thinks y follows x"


def test_language_detection():
    assert detect_language("The loop never ends because i is never incremented.") == "en"
    assert detect_language("Walang katapusan ang loop kasi hindi nadadagdagan ang i.") == "fil"
    assert detect_language("Infinite loop siya kasi hindi na-increment yung i, so the condition is always true.") == "taglish"
    assert detect_language("x = 5; y = x; print(y)") == "en"
    for case in CASES.values():
        assert detect_language(case["en"]) == "en"
        assert detect_language(case["taglish"]) == "taglish"


@pytest.mark.parametrize("word,expected", [
    ("inuulit", "again"), ("paulit-ulit", "repeatedly"), ("bumabalik", "return"), ("ibinalik", "return"),
    ("ibalik", "return"), ("nilalaktawan", "skip"), ("patakbuhin", "run"), ("dinadagdagan", "add"),
    ("idagdag", "add"), ("kondisyon", "condition"), ("totoo", "true"), ("mali", "false"), ("hanggang", "until"),
    ("bawat", "each"), ("dahil", "because"), ("kung", "if"), ("listahan", "list"), ("hanay", "array"),
    ("haba", "length"), ("sukat", "size"), ("numero", "number"), ("bilang", "number"),
    ("nagpi-print", "print"), ("i-assign", "assign"), ("nagre-return", "return"), ("nagprint", "print"),
])
def test_glossary_and_affix_stemming(word, expected):
    got = lemma(word)
    assert got is not None and got[1].split("|")[0] == expected, (word, got)


def test_code_and_english_terms_are_kept_as_written():
    g = gloss("Kapag i < 5 ang kondisyon, tinatawag ang acc.append(x) sa bawat ikot ng loop.")
    assert "i < 5" in g.primary and "acc.append(x)" in g.primary
    assert "condition" in g.primary and "each iteration" in g.primary and "loop" in g.primary
    assert "walang katapusan" not in gloss("Walang katapusan ang while loop").primary
    assert "infinite" in gloss("Walang katapusan ang while loop").primary


def _q(title):
    with SessionLocal() as db:
        return db.query(Question).filter_by(title=title).first().id


def test_api_returns_language_and_filipino_note(client):
    h = auth(pid="filipino-api")
    qid = _q("Copying a value")
    fb = client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": CASES["Copying a value"]["taglish"]}).json()["feedback"]
    assert fb["answer_language"] == "taglish" and fb["language_note"] == TAGLISH_NOTE
    assert fb["verdict"] == "correct"
    fb = client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": CASES["Copying a value"]["fil"]}).json()["feedback"]
    assert fb["answer_language"] == "fil" and fb["language_note"] == FILIPINO_NOTE
    fb = client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": CASES["Copying a value"]["en"]}).json()["feedback"]
    assert fb["answer_language"] == "en" and fb["language_note"] is None


def test_minimum_length_still_applies_to_filipino(client):
    h = auth(pid="filipino-short")
    qid = _q("Copying a value")
    assert client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "Lima po"}).status_code == 422
    assert client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "   ewan   "}).status_code == 422
    assert client.post("/api/responses", headers=h, json={"question_id": qid, "answer_text": "Ang lalabas ay 5."}).status_code == 201


def test_english_reference_answers_are_never_mistaken_for_filipino():
    wrong = [q["title"] for q in SEED_QUESTIONS if detect_language(q["rubric"]["reference_answer"]) != "en"]
    assert wrong == []
