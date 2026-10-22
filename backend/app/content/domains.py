"""Programming-reasoning skill domains tracked by the adaptive engine."""

DOMAINS = [
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
]

LANGUAGES = [
    {"slug": "python", "name": "Python"},
    {"slug": "javascript", "name": "JavaScript"},
]
