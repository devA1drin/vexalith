""""How to solve it" help for the browser coding exercises.

The help is written once per *concept* (the same problem exists in several
languages) and filled in with each language's own tools, so a Java learner reads
about a HashMap and a Python learner about a dictionary.

Each concept has:
- ``hints``: 3 progressive hints, revealed one at a time (a nudge, the key idea,
  then the concrete technique);
- ``idea``: the core concept in plain words;
- ``approach``: the general strategy in a few steps, not tied to code lines;
- ``pitfalls``: common mistakes and edge cases;
- ``pattern``: the reusable takeaway for similar problems;
- ``comment``: 1-2 short comment lines put on top of the reference solution.

Nothing here is a line-by-line walkthrough on purpose: the goal is the idea you
can reuse, not a narration of one particular program.
"""

from __future__ import annotations

# Language vocabulary used in the texts below.
TOOLS = {
    "python": {
        "map": "a dictionary", "set": "a set", "lower": "text.lower()", "split": "text.split()",
        "append": "out.append(x)", "get": "counts.get(word, 0)", "isint": "isinstance(x, list)",
        "upper": "w[0].upper()", "mod": "i % 3 == 0",
    },
    "javascript": {
        "map": "a Map (or a plain object)", "set": "a Set", "lower": "text.toLowerCase()", "split": "text.split(' ')",
        "append": "out.push(x)", "get": "(counts[word] || 0)", "isint": "Array.isArray(x)",
        "upper": "w[0].toUpperCase()", "mod": "i % 3 === 0",
    },
    "cpp": {
        "map": "a map / unordered_map", "set": "an unordered_set", "lower": "tolower() on each character",
        "split": "a stringstream (ss >> word)", "append": "out.push_back(x)", "get": "counts[word]++ (missing keys start at 0)",
        "isint": "", "upper": "toupper()", "mod": "i % 3 == 0",
    },
    "java": {
        "map": "a HashMap", "set": "a HashSet", "lower": "text.toLowerCase()", "split": "text.split(\" \")",
        "append": "list.add(x)", "get": "counts.getOrDefault(word, 0)", "isint": "", "upper": "Character.toUpperCase()",
        "mod": "i % 3 == 0",
    },
    "php": {
        "map": "an associative array", "set": "an array whose keys are the values you've seen", "lower": "strtolower($text)",
        "split": "explode(' ', $text)", "append": "$out[] = $x", "get": "($counts[$word] ?? 0)", "isint": "is_array($x)",
        "upper": "ucfirst()", "mod": "$i % 3 === 0",
    },
}

GUIDES: dict[str, dict] = {
    "sum-list": {
        "hints": [
            "Think about how you'd add a long list of numbers on paper: you keep one running number in your head.",
            "Start a total at 0, then visit every number once and add it to the total.",
            "A plain loop over the list does it. Because the total starts at 0, an empty list already returns 0 with no special case.",
        ],
        "idea": "Adding up a collection is an accumulation: one variable carries the answer so far and every item updates it.",
        "approach": [
            "Pick the starting value that is right for \"no items yet\" (0 for a sum).",
            "Go through the items one at a time.",
            "Fold each item into the running value.",
            "Return the running value after the last item.",
        ],
        "pitfalls": [
            "Starting the total at the first item instead of 0 breaks on an empty list.",
            "Resetting the total inside the loop, so only the last number survives.",
            "Returning from inside the loop, which stops after the first item.",
        ],
        "pattern": "Accumulator: start with the neutral value, combine each item, return. The same shape gives a product (start at 1), a count, or a longest string.",
        "comment": "Accumulator: start at 0 and add every number once.",
    },
    "reverse-string": {
        "hints": [
            "The last character of the answer is the first character of the input. Where does each character end up?",
            "Read the text from its end to its start and build the new text in that order.",
            "Either loop from the last index down to 0, or use the language's built-in way to reverse a sequence.",
        ],
        "idea": "Reversing means reading the same characters in the opposite order: position i moves to position (length - 1 - i).",
        "approach": [
            "Decide whether to build a new string or swap characters in place.",
            "Walk the characters from the end towards the start (or swap the outermost pair and move inwards).",
            "Stop when you've covered every character once, and return the result.",
        ],
        "pitfalls": [
            "Off-by-one: the last index is length - 1, not length.",
            "Forgetting the empty string, which should simply come back empty.",
            "Swapping in place but walking all the way across, which swaps everything back.",
        ],
        "pattern": "Two ends meeting in the middle, or reading backwards. The same idea reverses arrays and checks palindromes.",
        "comment": "Read the characters from the end to the start.",
    },
    "count-vowels": {
        "hints": [
            "You need to look at every character and decide: vowel or not?",
            "Keep a counter. Make the check case-insensitive so 'A' and 'a' are treated the same.",
            "Lower-case each character (or the whole text with {lower}) and test whether it is one of \"aeiou\".",
        ],
        "idea": "Counting the items that match a rule: scan everything once and add 1 whenever the rule is true.",
        "approach": [
            "Normalise the input so the rule is simple (here: make everything lower case).",
            "Look at each character once.",
            "Add 1 to a counter when the character is in the set of vowels.",
            "Return the counter.",
        ],
        "pitfalls": [
            "Missing upper-case vowels because the check is case-sensitive.",
            "Treating 'y' as a vowel when the task only lists a, e, i, o, u.",
            "Counting spaces or punctuation by accident.",
        ],
        "pattern": "Filter and count: a loop, a yes/no test and a counter. Swap the test to count digits, words or anything else.",
        "comment": "Count the characters that pass a test (lower-case, then check against \"aeiou\").",
    },
    "fizzbuzz": {
        "hints": [
            "Go through the numbers 1 to n and decide what to write for each one.",
            "Some numbers are multiples of both 3 and 5. Which check has to come first so they get \"FizzBuzz\"?",
            "Use the remainder operator ({mod} means \"multiple of 3\"). Check 15 (both) first, then 3, then 5, otherwise the number as text.",
        ],
        "idea": "Map every number to a label using ordered rules, where the most specific rule must win.",
        "approach": [
            "Loop over the range 1..n inclusive.",
            "Check the rules from most specific to least specific.",
            "Add exactly one label per number to the result list.",
            "Return the list (empty when n is 0).",
        ],
        "pitfalls": [
            "Checking 3 before 15, so 15 becomes \"Fizz\" instead of \"FizzBuzz\".",
            "Starting at 0 or stopping at n - 1 (off by one).",
            "Adding the number itself instead of the number as text.",
        ],
        "pattern": "Ordered rules: when conditions overlap, test the most specific case first. It shows up in pricing rules, grading scales and input validation.",
        "comment": "Most specific rule first: both 3 and 5, then 3, then 5, else the number.",
    },
    "largest": {
        "hints": [
            "Imagine flipping through cards and remembering only the biggest one you've seen.",
            "Start with the first number as the \"best so far\", then compare every other number with it.",
            "Whenever a number is bigger than the best so far, it becomes the new best. Return the best at the end.",
        ],
        "idea": "Finding a maximum is a running comparison: you only need to remember the best value seen so far.",
        "approach": [
            "Use the first item as the current best (the list is never empty).",
            "Visit each remaining item.",
            "Replace the best when an item beats it.",
            "Return the best after the loop.",
        ],
        "pitfalls": [
            "Starting the best at 0, which is wrong when every number is negative.",
            "Comparing neighbouring items instead of comparing with the best so far.",
        ],
        "pattern": "Running best: keep one candidate and update it when something better appears. It also finds the minimum, the longest word or the earliest date.",
        "comment": "Running best: start with the first number and keep whichever is bigger.",
    },
    "palindrome": {
        "hints": [
            "A palindrome looks the same from both ends. What would you compare?",
            "First clean the text: remove spaces and make it all one case, so \"Never odd or even\" can match.",
            "Compare the cleaned text with its reverse, or compare characters from both ends moving inwards.",
        ],
        "idea": "A palindrome is a sequence equal to its own reverse, after you remove the differences that shouldn't count.",
        "approach": [
            "Normalise the input (drop spaces, make it one case).",
            "Compare the first and last characters, then move both ends inwards.",
            "Return false as soon as a pair differs; true if the ends meet.",
        ],
        "pitfalls": [
            "Forgetting to ignore case or spaces, so real palindromes fail.",
            "Not deciding what the empty string is (it reads the same both ways, so true).",
            "Moving the two ends past each other and comparing pairs twice (harmless but wasteful).",
        ],
        "pattern": "Normalise, then compare from both ends. Cleaning input before checking it is a habit worth keeping for any text comparison.",
        "comment": "Clean the text (no spaces, one case), then compare it from both ends.",
    },
    "word-count": {
        "hints": [
            "You need to remember a number for each different word. What structure stores \"word → count\"?",
            "Make the text lower case and split it into words, then go through the words one by one.",
            "Use {map}: for each word, set its count to the old count (or 0 if it's new) plus 1, e.g. with {get}.",
        ],
        "idea": "Counting how often things appear is a frequency table: a map from each item to the number of times you've seen it.",
        "approach": [
            "Normalise the text so \"Go\" and \"go\" are the same word.",
            "Split it into words.",
            "For each word, add 1 to its entry in the map (a new word starts at 0).",
            "Return the map.",
        ],
        "pitfalls": [
            "Reading a missing key without a default, which errors or gives the wrong value.",
            "Forgetting to lower-case, so \"Go\" and \"go\" are counted separately.",
            "Counting empty strings when the text is empty or has extra spaces.",
        ],
        "pattern": "Frequency map: item → count, filled in one pass. It's the base for anagrams, most-common-item and duplicate detection.",
        "comment": "Frequency map: lower-case, split into words, add 1 per word.",
    },
    "unique": {
        "hints": [
            "As you go through the items, you need to know whether you've met each one before.",
            "Keep two things: the result list, and a record of the items you've already seen.",
            "Use {set} for the \"seen\" record: it answers \"have I seen this?\" quickly. Add an item to the result only the first time.",
        ],
        "idea": "Removing duplicates while keeping order means keeping the first time each value appears and skipping repeats.",
        "approach": [
            "Create an empty result and an empty \"seen\" collection.",
            "Go through the items in order.",
            "If an item hasn't been seen, add it to both; otherwise skip it.",
            "Return the result.",
        ],
        "pitfalls": [
            "Searching the result list each time instead of a set: correct, but slow on big inputs.",
            "Sorting or using a plain set as the answer, which loses the original order.",
            "Changing the list while looping over it.",
        ],
        "pattern": "Seen-set: one pass plus a set of what you've met. It also detects duplicates and finds the first repeated item.",
        "comment": "Keep a set of items already seen; add an item to the result only the first time.",
    },
    "two-sum": {
        "hints": [
            "For each number, think about which other number it would need to reach the target.",
            "If the current number is n, you're looking for target - n. Have you already passed it?",
            "Keep {map} from each number you've seen to its index. Before storing the current number, look up target - n; if it's there, you have both indexes.",
        ],
        "idea": "Instead of trying every pair, remember what you've seen so each number can ask \"is my partner already here?\" in one step.",
        "approach": [
            "Walk the list once, keeping a map from value to index.",
            "For each number, compute the partner it needs (target minus the number).",
            "If the partner is in the map, return the partner's index and the current index.",
            "Otherwise store the current number and keep going.",
        ],
        "pitfalls": [
            "Storing the number before checking, so a number can pair with itself (e.g. target 10 with a single 5).",
            "Returning the values instead of the indexes, or the indexes in the wrong order.",
            "Two nested loops: correct, but it slows down a lot on long lists.",
        ],
        "pattern": "Complement lookup: trade a little memory (a map) for speed, turning \"check every pair\" into one pass. It works for any \"find two things that fit together\" problem.",
        "comment": "Complement lookup: for each number, check whether target - n was already seen.",
    },
    "fibonacci": {
        "hints": [
            "Each Fibonacci number is the sum of the two before it. Which values do you actually need to keep?",
            "The textbook recursive version recomputes the same values again and again, which is far too slow for n = 80.",
            "Keep just two variables, the previous and the current number, and move them forward n times.",
        ],
        "idea": "When each step only depends on the last couple of results, you can build the answer from the bottom up and forget older values.",
        "approach": [
            "Start from the known base cases (0 and 1).",
            "Repeat n times: the next value is the sum of the two you hold, then shift the pair forward.",
            "Return the value that corresponds to n.",
        ],
        "pitfalls": [
            "Plain recursion grows exponentially and times out.",
            "Off-by-one: check that fib(0) is 0 and fib(1) is 1.",
            "A number type that is too small: large Fibonacci numbers need 64-bit integers.",
        ],
        "pattern": "Bottom-up (iterative) dynamic programming: compute small cases first and keep only what the next step needs.",
        "comment": "Bottom-up: keep only the last two numbers and step forward n times.",
    },
    "binary-search": {
        "hints": [
            "The list is sorted. If you look at the middle item, what does it tell you about the half you can ignore?",
            "Keep a low and a high boundary. Look at the middle: if it's too small, the target can only be to the right; too big, to the left.",
            "Loop while low <= high: compute mid, return it if it matches, otherwise move low to mid + 1 or high to mid - 1. Return -1 when the range is empty.",
        ],
        "idea": "Because the data is sorted, one comparison with the middle rules out half of what's left, so even huge lists take only a few steps.",
        "approach": [
            "Track the range that could still contain the target.",
            "Check the middle of that range.",
            "Shrink the range to the half that can still hold the target.",
            "Stop when you find it or the range becomes empty.",
        ],
        "pitfalls": [
            "Using low < high instead of low <= high, which misses the last remaining item.",
            "Setting low = mid or high = mid, which can loop forever.",
            "Forgetting the empty list and the \"not found\" case (-1).",
        ],
        "pattern": "Halving the search space: whenever a yes/no question splits the possibilities in order, binary search applies (sorted lists, guessing games, finding a threshold).",
        "comment": "Halve the range each step: compare with the middle, keep the half that can hold the target.",
    },
    "flatten": {
        "hints": [
            "A list can contain lists, which can contain lists… What do you do with an item that is itself a list?",
            "Handle the simple case (a plain value: add it) and the nested case (a list: flatten it first, then add what comes back).",
            "Call your own function on any nested list (check it with {isint}) and add its results to the output.",
        ],
        "idea": "Nested data has the same shape at every level, so a function can solve one level and call itself for the levels inside.",
        "approach": [
            "Go through the items of the current list.",
            "A plain value goes straight into the result.",
            "A nested list is flattened by the same function, and its items are added to the result.",
            "Return the result; an empty list naturally gives an empty result.",
        ],
        "pitfalls": [
            "Only flattening one level deep.",
            "Adding the nested result as one item instead of adding its items.",
            "Missing the base case, so the recursion never stops.",
        ],
        "pattern": "Recursion on nested structures: handle the simple item, recurse on the container. Folders, comment threads and JSON all have this shape.",
        "comment": "Recursion: plain values go in directly, nested lists are flattened by the same function.",
    },
    "capitalize": {
        "hints": [
            "Work one word at a time. What should happen to the first letter, and to the rest?",
            "Split the text into words, fix each word, then join them back with single spaces.",
            "For each word: upper-case the first character ({upper}), lower-case the rest, and skip empty words safely.",
        ],
        "idea": "Transforming text word by word: split it into pieces, change each piece the same way, then put it back together.",
        "approach": [
            "Split the text on spaces.",
            "Apply the same change to every word.",
            "Join the words with the same separator you split on.",
        ],
        "pitfalls": [
            "Only upper-casing the first letter and leaving \"hELLO\" as \"HELLO\".",
            "Crashing on an empty word or empty text.",
            "Joining with a different separator and changing the spacing.",
        ],
        "pattern": "Split → transform each piece → join. It's how you build slugs, initials, CSV clean-ups and more.",
        "comment": "Split into words, fix each word (first letter up, rest down), join with spaces.",
    },
}
GUIDES["sum-array"] = GUIDES["sum-list"]


def concept_of(slug: str) -> str:
    return slug.split("-", 1)[1]


def _fill(text: str, language: str) -> str:
    return text.format(**TOOLS[language])


def hints_for(slug: str, language: str) -> list[str]:
    return [_fill(h, language) for h in GUIDES[concept_of(slug)]["hints"]]


def explanation_for(slug: str, language: str) -> dict:
    g = GUIDES[concept_of(slug)]
    return {
        "idea": _fill(g["idea"], language),
        "approach": [_fill(s, language) for s in g["approach"]],
        "pitfalls": [_fill(s, language) for s in g["pitfalls"]],
        "pattern": _fill(g["pattern"], language),
    }


def commented_solution(slug: str, language: str, solution: str) -> str:
    """The reference solution with a short comment on top (no line-by-line notes)."""
    mark = "#" if language == "python" else "//"
    note = f"{mark} {GUIDES[concept_of(slug)]['comment']}\n"
    if solution.startswith("<?php\n"):
        return "<?php\n" + note + solution[len("<?php\n"):]
    return note + solution
