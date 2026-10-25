"""Hands-on coding exercises that learners run in their own browser.

Code is executed client-side only (Pyodide for Python, a locked-down Web Worker
for JavaScript; see exercises_more.py for C++, Java and PHP). The server never runs learner code: it sends the test inputs,
and for hidden tests it only compares the outputs the browser reports against
expected values it keeps to itself.

Each test is ``(args, expected)``; ``args`` is the list of arguments passed to
the function. Values must be JSON (numbers, strings, booleans, lists, objects).
The first ``visible`` tests are shown to the learner; the rest are hidden.
"""

from __future__ import annotations

RUNNABLE_LANGUAGES = ("python", "javascript", "cpp", "java", "php")
COMING_SOON_LANGUAGES: tuple[str, ...] = ()


def _ex(slug, language, difficulty, title, description, function, starter, solution, tests, visible=2, timeout_ms=4000):
    return {
        "slug": slug, "language": language, "difficulty": difficulty, "title": title,
        "description": description, "function": function, "starter": starter, "solution": solution,
        "tests": [{"args": a, "expected": e} for a, e in tests], "visible": visible, "timeout_ms": timeout_ms,
    }


PY_EXERCISES = [
    _ex("py-sum-list", "python", "beginner", "Add up a list",
        "Write `total(nums)` that returns the sum of all numbers in the list. An empty list adds up to 0. Try it with a loop instead of the built-in sum().",
        "total", "def total(nums):\n    # add each number to a running total\n    result = 0\n    return result\n",
        "def total(nums):\n    result = 0\n    for n in nums:\n        result += n\n    return result\n",
        [([[1, 2, 3]], 6), ([[]], 0), ([[-5, 5, 10]], 10), ([[100]], 100), ([[0, 0, 0]], 0)]),
    _ex("py-reverse-string", "python", "beginner", "Reverse a word",
        "Write `reverse(text)` that returns the text backwards, so 'abc' becomes 'cba'.",
        "reverse", "def reverse(text):\n    return text\n",
        "def reverse(text):\n    return text[::-1]\n",
        [(["abc"], "cba"), (["racecar"], "racecar"), ([""], ""), (["Hi!"], "!iH")]),
    _ex("py-count-vowels", "python", "beginner", "Count the vowels",
        "Write `count_vowels(text)` that returns how many vowels (a, e, i, o, u) are in the text. Upper-case vowels count too.",
        "count_vowels", "def count_vowels(text):\n    count = 0\n    return count\n",
        "def count_vowels(text):\n    return sum(1 for ch in text.lower() if ch in 'aeiou')\n",
        [(["hello"], 2), (["AEIOU"], 5), (["rhythm"], 0), ([""], 0), (["Programming is fun"], 5)]),
    _ex("py-fizzbuzz", "python", "beginner", "FizzBuzz list",
        "Write `fizzbuzz(n)` that returns a list of strings for 1..n: 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for both, otherwise the number as text.",
        "fizzbuzz", "def fizzbuzz(n):\n    out = []\n    for i in range(1, n + 1):\n        pass  # your code here\n    return out\n",
        "def fizzbuzz(n):\n    out = []\n    for i in range(1, n + 1):\n        if i % 15 == 0:\n            out.append('FizzBuzz')\n        elif i % 3 == 0:\n            out.append('Fizz')\n        elif i % 5 == 0:\n            out.append('Buzz')\n        else:\n            out.append(str(i))\n    return out\n",
        [([5], ["1", "2", "Fizz", "4", "Buzz"]), ([1], ["1"]), ([15], ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]), ([0], [])]),
    _ex("py-largest", "python", "beginner", "Find the largest number",
        "Write `largest(nums)` that returns the biggest number in a non-empty list, without using max().",
        "largest", "def largest(nums):\n    best = nums[0]\n    return best\n",
        "def largest(nums):\n    best = nums[0]\n    for n in nums[1:]:\n        if n > best:\n            best = n\n    return best\n",
        [([[3, 9, 2]], 9), ([[-4, -2, -7]], -2), ([[5]], 5), ([[1, 1, 1]], 1)]),
    _ex("py-palindrome", "python", "intermediate", "Is it a palindrome?",
        "Write `is_palindrome(text)` that returns True when the text reads the same forwards and backwards, ignoring spaces and upper/lower case.",
        "is_palindrome", "def is_palindrome(text):\n    return False\n",
        "def is_palindrome(text):\n    clean = text.replace(' ', '').lower()\n    return clean == clean[::-1]\n",
        [(["racecar"], True), (["hello"], False), (["Never odd or even"], True), ([""], True), (["ab"], False)]),
    _ex("py-word-count", "python", "intermediate", "Count words",
        "Write `word_count(text)` that returns a dictionary mapping each lower-case word to how many times it appears. Words are separated by spaces.",
        "word_count", "def word_count(text):\n    counts = {}\n    return counts\n",
        "def word_count(text):\n    counts = {}\n    for w in text.lower().split():\n        counts[w] = counts.get(w, 0) + 1\n    return counts\n",
        [(["the cat the hat"], {"the": 2, "cat": 1, "hat": 1}), ([""], {}), (["Go go GO"], {"go": 3})]),
    _ex("py-unique", "python", "intermediate", "Remove duplicates, keep order",
        "Write `unique(items)` that returns a new list without duplicates, keeping the first time each item appears.",
        "unique", "def unique(items):\n    return items\n",
        "def unique(items):\n    seen = set()\n    out = []\n    for x in items:\n        if x not in seen:\n            seen.add(x)\n            out.append(x)\n    return out\n",
        [([[1, 2, 1, 3, 2]], [1, 2, 3]), ([[]], []), ([["b", "a", "b"]], ["b", "a"]), ([[7, 7, 7]], [7])]),
    _ex("py-two-sum", "python", "intermediate", "Two numbers that add up",
        "Write `two_sum(nums, target)` that returns the indexes [i, j] (i < j) of the two numbers that add up to target. There is always exactly one answer. Can you do it in one pass with a dictionary?",
        "two_sum", "def two_sum(nums, target):\n    return [0, 0]\n",
        "def two_sum(nums, target):\n    seen = {}\n    for j, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], j]\n        seen[n] = j\n",
        [([[2, 7, 11, 15], 9], [0, 1]), ([[3, 2, 4], 6], [1, 2]), ([[1, 5, 5], 10], [1, 2]), ([[0, -3, 8, 3], 0], [1, 3])]),
    _ex("py-fibonacci", "python", "intermediate", "Fibonacci number",
        "Write `fib(n)` that returns the n-th Fibonacci number, where fib(0) = 0 and fib(1) = 1. Make it fast enough for n = 80 (no slow recursion).",
        "fib", "def fib(n):\n    return n\n",
        "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n",
        [([0], 0), ([1], 1), ([10], 55), ([30], 832040), ([80], 23416728348467685)]),
    _ex("py-binary-search", "python", "advanced", "Binary search",
        "Write `search(nums, target)` for a sorted list that returns the index of target, or -1 if it isn't there. Cut the search range in half each step.",
        "search", "def search(nums, target):\n    lo, hi = 0, len(nums) - 1\n    return -1\n",
        "def search(nums, target):\n    lo, hi = 0, len(nums) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n",
        [([[1, 3, 5, 7, 9], 7], 3), ([[1, 3, 5], 4], -1), ([[], 1], -1), ([[2], 2], 0), ([list(range(0, 1000, 2)), 998], 499)]),
    _ex("py-flatten", "python", "advanced", "Flatten nested lists",
        "Write `flatten(items)` that turns a list that may contain lists (at any depth) into one flat list, in order.",
        "flatten", "def flatten(items):\n    out = []\n    return out\n",
        "def flatten(items):\n    out = []\n    for x in items:\n        if isinstance(x, list):\n            out.extend(flatten(x))\n        else:\n            out.append(x)\n    return out\n",
        [([[1, [2, 3], 4]], [1, 2, 3, 4]), ([[[[[]]]]], []), ([[1, [2, [3, [4]]]]], [1, 2, 3, 4]), ([["a", ["b"]]], ["a", "b"])]),
]

JS_EXERCISES = [
    _ex("js-sum-array", "javascript", "beginner", "Add up an array",
        "Write `total(nums)` that returns the sum of all numbers in the array. An empty array adds up to 0. Use a loop.",
        "total", "function total(nums) {\n  let result = 0;\n  return result;\n}\n",
        "function total(nums) {\n  let result = 0;\n  for (const n of nums) result += n;\n  return result;\n}\n",
        [([[1, 2, 3]], 6), ([[]], 0), ([[-5, 5, 10]], 10), ([[100]], 100)]),
    _ex("js-reverse-string", "javascript", "beginner", "Reverse a word",
        "Write `reverse(text)` that returns the text backwards, so 'abc' becomes 'cba'.",
        "reverse", "function reverse(text) {\n  return text;\n}\n",
        "function reverse(text) {\n  return text.split('').reverse().join('');\n}\n",
        [(["abc"], "cba"), ([""], ""), (["Hi!"], "!iH"), (["level"], "level")]),
    _ex("js-count-vowels", "javascript", "beginner", "Count the vowels",
        "Write `countVowels(text)` that returns how many vowels (a, e, i, o, u) are in the text, upper or lower case.",
        "countVowels", "function countVowels(text) {\n  let count = 0;\n  return count;\n}\n",
        "function countVowels(text) {\n  return [...text.toLowerCase()].filter((c) => 'aeiou'.includes(c)).length;\n}\n",
        [(["hello"], 2), (["AEIOU"], 5), (["rhythm"], 0), (["JavaScript is fun"], 5)]),
    _ex("js-fizzbuzz", "javascript", "beginner", "FizzBuzz array",
        "Write `fizzbuzz(n)` that returns an array of strings for 1..n: 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for both, otherwise the number as text.",
        "fizzbuzz", "function fizzbuzz(n) {\n  const out = [];\n  for (let i = 1; i <= n; i++) {\n    // your code here\n  }\n  return out;\n}\n",
        "function fizzbuzz(n) {\n  const out = [];\n  for (let i = 1; i <= n; i++) {\n    out.push(i % 15 === 0 ? 'FizzBuzz' : i % 3 === 0 ? 'Fizz' : i % 5 === 0 ? 'Buzz' : String(i));\n  }\n  return out;\n}\n",
        [([5], ["1", "2", "Fizz", "4", "Buzz"]), ([1], ["1"]), ([15], ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]), ([0], [])]),
    _ex("js-largest", "javascript", "beginner", "Find the largest number",
        "Write `largest(nums)` that returns the biggest number in a non-empty array, without Math.max.",
        "largest", "function largest(nums) {\n  let best = nums[0];\n  return best;\n}\n",
        "function largest(nums) {\n  let best = nums[0];\n  for (const n of nums) if (n > best) best = n;\n  return best;\n}\n",
        [([[3, 9, 2]], 9), ([[-4, -2, -7]], -2), ([[5]], 5), ([[1, 1, 1]], 1)]),
    _ex("js-palindrome", "javascript", "intermediate", "Is it a palindrome?",
        "Write `isPalindrome(text)` that returns true when the text reads the same forwards and backwards, ignoring spaces and upper/lower case.",
        "isPalindrome", "function isPalindrome(text) {\n  return false;\n}\n",
        "function isPalindrome(text) {\n  const c = text.replaceAll(' ', '').toLowerCase();\n  return c === [...c].reverse().join('');\n}\n",
        [(["racecar"], True), (["hello"], False), (["Never odd or even"], True), ([""], True), (["ab"], False)]),
    _ex("js-word-count", "javascript", "intermediate", "Count words",
        "Write `wordCount(text)` that returns an object mapping each lower-case word to how many times it appears. Words are separated by spaces.",
        "wordCount", "function wordCount(text) {\n  const counts = {};\n  return counts;\n}\n",
        "function wordCount(text) {\n  const counts = {};\n  for (const w of text.toLowerCase().split(' ').filter(Boolean)) counts[w] = (counts[w] ?? 0) + 1;\n  return counts;\n}\n",
        [(["the cat the hat"], {"the": 2, "cat": 1, "hat": 1}), ([""], {}), (["Go go GO"], {"go": 3})]),
    _ex("js-unique", "javascript", "intermediate", "Remove duplicates, keep order",
        "Write `unique(items)` that returns a new array without duplicates, keeping the first time each item appears.",
        "unique", "function unique(items) {\n  return items;\n}\n",
        "function unique(items) {\n  return [...new Set(items)];\n}\n",
        [([[1, 2, 1, 3, 2]], [1, 2, 3]), ([[]], []), ([["b", "a", "b"]], ["b", "a"]), ([[7, 7, 7]], [7])]),
    _ex("js-two-sum", "javascript", "intermediate", "Two numbers that add up",
        "Write `twoSum(nums, target)` that returns the indexes [i, j] (i < j) of the two numbers that add up to target. There is always exactly one answer. Try one pass with a Map.",
        "twoSum", "function twoSum(nums, target) {\n  return [0, 0];\n}\n",
        "function twoSum(nums, target) {\n  const seen = new Map();\n  for (let j = 0; j < nums.length; j++) {\n    if (seen.has(target - nums[j])) return [seen.get(target - nums[j]), j];\n    seen.set(nums[j], j);\n  }\n}\n",
        [([[2, 7, 11, 15], 9], [0, 1]), ([[3, 2, 4], 6], [1, 2]), ([[1, 5, 5], 10], [1, 2]), ([[0, -3, 8, 3], 0], [1, 3])]),
    _ex("js-capitalize", "javascript", "intermediate", "Capitalize each word",
        "Write `titleCase(text)` that makes the first letter of every word upper case and the rest lower case. Words are separated by single spaces.",
        "titleCase", "function titleCase(text) {\n  return text;\n}\n",
        "function titleCase(text) {\n  return text.split(' ').map((w) => w ? w[0].toUpperCase() + w.slice(1).toLowerCase() : w).join(' ');\n}\n",
        [(["hello world"], "Hello World"), (["jAVA sCRIPT"], "Java Script"), ([""], ""), (["a"], "A")]),
    _ex("js-binary-search", "javascript", "advanced", "Binary search",
        "Write `search(nums, target)` for a sorted array that returns the index of target, or -1 if it isn't there. Halve the range each step.",
        "search", "function search(nums, target) {\n  let lo = 0, hi = nums.length - 1;\n  return -1;\n}\n",
        "function search(nums, target) {\n  let lo = 0, hi = nums.length - 1;\n  while (lo <= hi) {\n    const mid = (lo + hi) >> 1;\n    if (nums[mid] === target) return mid;\n    if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n  }\n  return -1;\n}\n",
        [([[1, 3, 5, 7, 9], 7], 3), ([[1, 3, 5], 4], -1), ([[], 1], -1), ([[2], 2], 0), ([list(range(0, 1000, 2)), 998], 499)]),
    _ex("js-flatten", "javascript", "advanced", "Flatten nested arrays",
        "Write `flatten(items)` that turns an array that may contain arrays (at any depth) into one flat array, in order, without using .flat().",
        "flatten", "function flatten(items) {\n  const out = [];\n  return out;\n}\n",
        "function flatten(items) {\n  const out = [];\n  for (const x of items) Array.isArray(x) ? out.push(...flatten(x)) : out.push(x);\n  return out;\n}\n",
        [([[1, [2, 3], 4]], [1, 2, 3, 4]), ([[[[[]]]]], []), ([[1, [2, [3, [4]]]]], [1, 2, 3, 4]), ([["a", ["b"]]], ["a", "b"])]),
]

# Topic of each exercise (same idea in both languages), shown as a chip and used to group the list.
TOPICS = {
    "sum-list": "Loops", "sum-array": "Loops", "largest": "Loops", "fizzbuzz": "Loops & conditions",
    "reverse-string": "Strings", "count-vowels": "Strings", "palindrome": "Strings", "capitalize": "Strings",
    "word-count": "Dictionaries & maps", "unique": "Lists & sets", "two-sum": "Hash maps",
    "fibonacci": "Loops & math", "binary-search": "Searching", "flatten": "Recursion",
}


for _e in PY_EXERCISES + JS_EXERCISES:
    _e["topic"] = TOPICS[_e["slug"].split("-", 1)[1]]

from app.content.exercises_more import build  # noqa: E402

MORE_EXERCISES = build(_ex)
EXERCISES = PY_EXERCISES + JS_EXERCISES + MORE_EXERCISES
BY_SLUG = {e["slug"]: e for e in EXERCISES}
