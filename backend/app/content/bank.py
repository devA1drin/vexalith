"""Aggregated seed bank (every question gets progressive hints, see hints.py)."""

from app.content.hints import with_hints
from app.content.humanize import with_human_prompts

from app.content.questions_algorithms import QUESTIONS_ALGORITHMS
from app.content.questions_cpp import QUESTIONS_CPP
from app.content.questions_css import QUESTIONS_CSS
from app.content.questions_fund_cpp import QUESTIONS_FUND_CPP
from app.content.questions_fund_java import QUESTIONS_FUND_JAVA
from app.content.questions_fund_javascript import QUESTIONS_FUND_JAVASCRIPT
from app.content.questions_fund_php import QUESTIONS_FUND_PHP
from app.content.questions_fund_python import QUESTIONS_FUND_PYTHON
from app.content.questions_fund_web import QUESTIONS_FUND_CSS, QUESTIONS_FUND_GENERAL, QUESTIONS_FUND_HTML
from app.content.questions_html import QUESTIONS_HTML
from app.content.questions_java import QUESTIONS_JAVA
from app.content.questions_logic import QUESTIONS_LOGIC
from app.content.questions_loops import QUESTIONS_LOOPS
from app.content.questions_missing_code import QUESTIONS_MISSING_CODE
from app.content.questions_oop import QUESTIONS_OOP
from app.content.questions_part1 import QUESTIONS_PART1
from app.content.questions_part2 import QUESTIONS_PART2
from app.content.questions_php import QUESTIONS_PHP

FUNDAMENTALS_QUESTIONS = (
    QUESTIONS_FUND_PYTHON
    + QUESTIONS_FUND_JAVASCRIPT
    + QUESTIONS_FUND_PHP
    + QUESTIONS_FUND_CPP
    + QUESTIONS_FUND_JAVA
    + QUESTIONS_FUND_HTML
    + QUESTIONS_FUND_CSS
    + QUESTIONS_FUND_GENERAL
)

SEED_QUESTIONS = with_human_prompts(with_hints(
    FUNDAMENTALS_QUESTIONS
    + QUESTIONS_PART1
    + QUESTIONS_PART2
    + QUESTIONS_HTML
    + QUESTIONS_CSS
    + QUESTIONS_PHP
    + QUESTIONS_CPP
    + QUESTIONS_JAVA
    + QUESTIONS_LOGIC
    + QUESTIONS_ALGORITHMS
    + QUESTIONS_LOOPS
    + QUESTIONS_MISSING_CODE
    + QUESTIONS_OOP
))
