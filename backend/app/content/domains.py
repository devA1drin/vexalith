"""Programming-reasoning skill domains tracked by the adaptive engine."""

DOMAINS = [
    {
        "slug": "fundamentals",
        "name": "Fundamentals",
        "description": (
            "Start from zero: variables, types, operators, strings, conditionals, loops, functions, "
            "lists and dictionaries, null values, errors; HTML/CSS basics; algorithms, binary and booleans."
        ),
    },
    {
        "slug": "code_tracing",
        "name": "Code Tracing & Comprehension",
        "description": "Read code precisely and predict its output and state changes.",
    },
    {
        "slug": "debugging",
        "name": "Debugging",
        "description": "Locate a bug, explain its root cause, and propose a correct fix.",
    },
    {
        "slug": "algorithmic_thinking",
        "name": "Algorithmic Thinking & Complexity",
        "description": "Reason about Big-O, compare approaches, and pick efficient algorithms.",
    },
    {
        "slug": "edge_cases_testing",
        "name": "Edge Cases & Testing",
        "description": "Find boundary conditions and design tests that would catch failures.",
    },
    {
        "slug": "code_review_design",
        "name": "Code Review & Design",
        "description": "Critique readability, correctness risks, tradeoffs, and design principles (SOLID).",
    },
    {
        "slug": "data_structures",
        "name": "Data Structures",
        "description": "Choose and reason about lists, sets, maps, stacks, queues, heaps, trees, and graphs.",
    },
    {
        "slug": "algorithms",
        "name": "Algorithms",
        "description": (
            "Classic problems — searching, sorting, two pointers, sliding window, recursion, dynamic "
            "programming, graphs and greedy: explain the approach, why it is correct, and its cost."
        ),
    },
    {
        "slug": "logic_problems",
        "name": "Logic Problems",
        "description": (
            "Language-agnostic reasoning: truth tables, boolean simplification, deduction, "
            "short-circuit conditionals, invariants, sets and sequences."
        ),
    },
]

LANGUAGES = [
    {"slug": "python", "name": "Python"},
    {"slug": "javascript", "name": "JavaScript"},
    {"slug": "php", "name": "PHP"},
    {"slug": "cpp", "name": "C++"},
    {"slug": "html", "name": "HTML"},
    {"slug": "css", "name": "CSS"},
    {"slug": "general", "name": "General"},
]

# Language-agnostic questions (logic puzzles, prose algorithm problems) use this
# language tag and are eligible under every language selection.
GENERAL = "general"
FUNDAMENTALS = "fundamentals"
LANGUAGE_SLUGS = [lang["slug"] for lang in LANGUAGES]
