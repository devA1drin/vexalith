"""Aggregated seed bank."""

from app.content.questions_algorithms import QUESTIONS_ALGORITHMS
from app.content.questions_css import QUESTIONS_CSS
from app.content.questions_html import QUESTIONS_HTML
from app.content.questions_logic import QUESTIONS_LOGIC
from app.content.questions_part1 import QUESTIONS_PART1
from app.content.questions_part2 import QUESTIONS_PART2
from app.content.questions_php import QUESTIONS_PHP

SEED_QUESTIONS = (
    QUESTIONS_PART1
    + QUESTIONS_PART2
    + QUESTIONS_HTML
    + QUESTIONS_CSS
    + QUESTIONS_PHP
    + QUESTIONS_LOGIC
    + QUESTIONS_ALGORITHMS
)
