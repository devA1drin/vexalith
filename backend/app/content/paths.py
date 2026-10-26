"""Learning paths: guided routes through the existing questions and coding exercises.

A path is an ordered list of steps, from beginner to advanced. Each step draws its questions
from a pool (languages x topics x levels) of the built-in question bank and may add one coding
exercise. ``exercise`` is either an exercise slug (``"py-fizzbuzz"``) or ``"any:<name>"``, which
accepts that exercise passed in any of the five coding languages.
"""

from __future__ import annotations

from dataclasses import dataclass, field

BEG, INT, ADV = "beginner", "intermediate", "advanced"
ALL_LEVELS = (BEG, INT, ADV)
CODE_LANGS = ("python", "javascript", "cpp", "java", "php")
PREFIX = {"python": "py", "javascript": "js", "cpp": "cpp", "java": "java", "php": "php"}

QUESTIONS_PER_STEP = 4  # a step's score is the average of its best answers, up to this many
PASS_MARK = 0.75  # 75%: between the 70-80% the brief asks for


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    blurb: str
    languages: tuple[str, ...]
    domains: tuple[str, ...]
    levels: tuple[str, ...] = ALL_LEVELS
    exercise: str | None = None
    questions: int = QUESTIONS_PER_STEP


@dataclass(frozen=True)
class Path:
    slug: str
    name: str
    blurb: str
    mark: str  # short code shown on the path's emblem
    steps: tuple[Step, ...] = field(default_factory=tuple)


def _sum_slug(lang: str) -> str:
    return "js-sum-array" if lang == "javascript" else f"{PREFIX[lang]}-sum-list"


def _language_path(lang: str, name: str, mark: str, blurb: str, notes: dict[str, str]) -> Path:
    p = PREFIX[lang]
    L = (lang,)
    return Path(lang, name, blurb, mark, (
        Step("first-steps", "First steps", notes["first"], L, ("fundamentals",), (BEG,), _sum_slug(lang)),
        Step("read-and-fix", "Read and fix code", "Follow code line by line, predict what it prints and find the bug.",
             L, ("code_tracing", "debugging"), (BEG, INT), f"{p}-reverse-string"),
        Step("decisions-loops", "Decisions and loops", notes["loops"], L, ("fundamentals",), (INT,), f"{p}-fizzbuzz"),
        Step("collections", "Collections and edge cases", "Lists, maps and stacks, and the empty or odd inputs that break them.",
             L, ("data_structures", "edge_cases_testing"), ALL_LEVELS, f"{p}-word-count"),
        Step("objects", "Classes and objects", notes["oop"], L, ("oop",), (BEG, INT)),
        Step("problem-solving", "Problem solving", "Searching, sorting and how much work a solution really does.",
             L, ("algorithms", "algorithmic_thinking"), (BEG, INT), f"{p}-two-sum"),
        Step("going-further", "Going further", "The advanced traps, plus reviewing code the way a senior would.",
             L, ("fundamentals", "code_review_design", "algorithms"), (ADV,), f"{p}-binary-search"),
    ))


PATHS: tuple[Path, ...] = (
    Path("fundamentals", "Programming Fundamentals",
         "Start here if you're new. Plain logic, binary and pseudocode, no single language needed.", "01", (
             Step("values-and-steps", "Values and steps", "Following instructions in order, simple rules and binary numbers.",
                  ("general",), ("fundamentals",), (BEG,), "any:sum-list"),
             Step("conditions-loops", "Conditions and loops", "AND, OR, and loops that halve, count and keep the largest.",
                  ("general",), ("fundamentals",), (INT,), "any:fizzbuzz"),
             Step("think-like-a-computer", "Think like the computer", "Nested loops, loops that never end and adding in binary.",
                  ("general",), ("fundamentals",), (ADV,), "any:largest"),
             Step("first-algorithms", "Your first algorithms", "Greedy change, shortest paths and keeping the best so far.",
                  ("general",), ("algorithms",), (BEG,), "any:reverse-string", 3),
         )),
    Path("web", "Web Basics",
         "HTML for structure and CSS for looks: pages that read well, work on phones and are easy to use.", "</>", (
             Step("html-first", "HTML first steps", "Page skeletons, headings, links and images with alt text.",
                  ("html",), ("fundamentals",), (BEG,)),
             Step("css-first", "CSS first steps", "Selectors, units, padding and margin.", ("css",), ("fundamentals",), (BEG,)),
             Step("read-markup", "Read and fix markup", "Predict how markup renders and spot what's broken.",
                  ("html",), ("code_tracing", "debugging"), (BEG, INT)),
             Step("styling", "Which rule wins", "Specificity, inheritance and laying things out with flexbox.",
                  ("css",), ("fundamentals", "code_tracing"), (INT,)),
             Step("fix-layouts", "Fix broken layouts", "z-index, heights, sticky headers and boxes that won't shrink.",
                  ("css",), ("debugging", "edge_cases_testing")),
             Step("clean-pages", "Clean, usable pages", "Forms with labels, real buttons and pages that hold up on small screens.",
                  ("html", "css"), ("fundamentals", "code_review_design"), (ADV,)),
         )),
    _language_path("python", "Python", "Py",
                   "From print and if to dictionaries, classes and clean algorithms, in the friendliest first language.",
                   {"first": "Variables, text input, the three kinds of division and print versus return.",
                    "loops": "Lists, dictionaries, break and continue, and whether and or or runs first.",
                    "oop": "Classes, self, inheritance and @property."}),
    _language_path("javascript", "JavaScript", "JS",
                   "The language of the browser: values, loops, objects and the quirks that catch people out.",
                   {"first": "let and const, == versus ===, and adding text to numbers.",
                    "loops": "Objects, ?? versus ||, parseInt and stopping a loop early.",
                    "oop": "Classes, this, private fields and extends."}),
    _language_path("cpp", "C++", "C++",
                   "Modern C++: types, references, containers and classes, with memory in mind.",
                   {"first": "cout and cin, whole-number division and your first loops.",
                    "loops": "References, vectors, std::string and breaking out early.",
                    "oop": "Encapsulation, initializer lists and virtual methods."}),
    _language_path("java", "Java", "J",
                   "Modern Java: strong types, classes from day one and the standard collections.",
                   {"first": "println, integer division, && and || and arrays.",
                    "loops": "== versus equals(), ArrayList, null and switch.",
                    "oop": "Fields, constructors, this, extends and super."}),
    _language_path("php", "PHP", "PHP",
                   "Server-side PHP: strings, arrays and functions that power real websites.",
                   {"first": "Quotes, the dollar sign, echo and arrays.",
                    "loops": "Associative arrays, loose comparisons, match and ??.",
                    "oop": "Classes, $this, visibility and parent::__construct."}),
    Path("oop", "Object-Oriented Programming",
         "Classes, objects and design across Python, JavaScript, C++, Java and PHP.", "{ }", (
             Step("classes", "Classes and objects", "Blueprint versus house: constructors, fields and separate instances.",
                  ("general", *CODE_LANGS), ("oop",), (BEG,)),
             Step("encapsulation", "Encapsulation and inheritance", "Hiding the inside, is-a versus has-a and calling the parent.",
                  ("general", *CODE_LANGS), ("oop",), (INT,)),
             Step("polymorphism", "Polymorphism and good design", "Overriding, interfaces, composition over inheritance and Liskov.",
                  ("general", *CODE_LANGS), ("oop",), (ADV,)),
             Step("design-review", "Design reviews", "Read real code and say what you'd change and why.",
                  CODE_LANGS, ("code_review_design",), (INT, ADV)),
         )),
    Path("logic", "Logic & Algorithms",
         "Puzzles, proofs and classic algorithms: the thinking behind code, in plain language.", "∴", (
             Step("logic-warmup", "Logic warm-up", "Implications, De Morgan, knights and knaves.", ("general",), ("logic_problems",), (BEG,)),
             Step("careful-reasoning", "Careful reasoning", "Invariants, pigeonholes, sets and who broke the build.",
                  ("general",), ("logic_problems",), (INT,)),
             Step("algorithm-basics", "Algorithm basics", "Build orders, weighted roads and counting steps.",
                  ("general",), ("algorithms",), (INT,), "any:two-sum"),
             Step("hard-puzzles", "Hard puzzles", "Lockers, mislabeled boxes, induction and proofs that loops stop.",
                  ("general",), ("logic_problems",), (ADV,)),
             Step("search-recursion", "Search and recursion", "When greedy fails, base cases and halving the search.",
                  ("general",), ("algorithms",), (ADV,), "any:binary-search", 2),
         )),
)

BY_SLUG: dict[str, Path] = {p.slug: p for p in PATHS}


def exercise_slugs(spec: str | None) -> list[str]:
    """The concrete exercise slugs that satisfy a step's exercise (one, or one per language)."""
    from app.content.exercises import BY_SLUG as EXERCISES

    if not spec:
        return []
    if spec.startswith("any:"):
        name = spec[4:]
        names = {"sum-list": "sum-array"}  # JavaScript calls its list an array
        slugs = []
        for lang in CODE_LANGS:
            slug = f"{PREFIX[lang]}-{name}"
            if slug not in EXERCISES and lang == "javascript" and name in names:
                slug = f"js-{names[name]}"
            if slug in EXERCISES:
                slugs.append(slug)
        return slugs
    return [spec] if spec in EXERCISES else []
