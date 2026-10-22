"""Seed questions: Code Tracing, Debugging, Algorithmic Thinking.

Each question carries a rubric used by the offline heuristic grader and as a
hint for the LLM grader:
  concepts:       [(label, [keywords...], weight)]  — ideas a correct answer should contain
  misconceptions: [(label, [keywords...], explanation)] — common wrong answers
  reference:      model answer shown after submission
"""

from app.content.qdef import Q

QUESTIONS_PART1 = [
    # ── Code Tracing ─────────────────────────────────────────────────────────
    Q("code_tracing", "beginner", "python", "Sum of evens",
      """nums = [1, 2, 3, 4]
total = 0
for n in nums:
    if n % 2 == 0:
        total += n
print(total)""",
      "What does this program print? Explain how you got there.",
      [("prints 6", ["6", "six"], 2), ("only even numbers are added", ["even", "2 and 4", "2 + 4", "% 2"], 1)],
      [("summed every element", ["10"], "10 is the sum of all elements; the `if n % 2 == 0` filter only lets 2 and 4 through.")],
      "It prints 6. The loop visits 1, 2, 3, 4 but only adds values where n % 2 == 0 (the evens 2 and 4), so total = 2 + 4 = 6."),
    Q("code_tracing", "beginner", "python", "Slicing a string",
      """s = "hello"
print(s[1:4], len(s), s[-1])""",
      "Predict the exact output and explain each part.",
      [("slice is 'ell'", ["ell"], 2), ("length is 5", ["5", "five"], 1), ("s[-1] is 'o'", ["'o'", '"o"', "5 o", "last char", "last letter"], 1),
       ("slice end is exclusive", ["exclusive", "not included", "up to but not", "stops before"], 1)],
      [("end index treated as inclusive", ["ello"], "Slices exclude the end index: s[1:4] takes indices 1, 2, 3 → 'ell'.")],
      "Output: `ell 5 o`. s[1:4] takes indices 1..3 (end exclusive) → 'ell'; len('hello') is 5; s[-1] is the last character 'o'."),
    Q("code_tracing", "beginner", "javascript", "Loop with continue",
      """let count = 0;
for (let i = 0; i < 5; i++) {
  if (i === 3) continue;
  count += i;
}
console.log(count);""",
      "What is logged? Walk through the iterations.",
      [("logs 7", ["7", "seven"], 2), ("continue skips i = 3", ["continue", "skip"], 1)],
      [("included 3", ["10"], "10 would include i = 3, but `continue` jumps to the next iteration before adding it.")],
      "It logs 7: 0 + 1 + 2 + 4. When i === 3, `continue` skips the addition."),
    Q("code_tracing", "beginner", "javascript", "Two names, one array",
      """const a = [3, 1, 2];
const b = a;
b.push(4);
console.log(a.length, a[0]);""",
      "What is printed, and why does changing `b` affect (or not affect) `a`?",
      [("prints 4 3", ["4 3", "4, 3", "length is 4", "length 4"], 2), ("same reference", ["reference", "same array", "alias", "same object", "points to"], 2)],
      [("assumed a copy", ["copy of a", "3 3", "a is unchanged", "a stays"], "`const b = a` copies the reference, not the array; both names point to the same array.")],
      "It prints `4 3`. `b = a` makes b reference the same array, so push(4) mutates the array seen through a too (length 4, first element still 3)."),

    Q("code_tracing", "intermediate", "python", "Mutable default argument",
      """def f(x, acc=[]):
    acc.append(x)
    return acc

print(f(1))
print(f(2))""",
      "Predict both lines of output and explain the behaviour.",
      [("second call prints [1, 2]", ["[1, 2]", "[1,2]"], 2),
       ("default list is created once and shared", ["mutable default", "default argument", "shared", "evaluated once", "same list", "once at definition", "created once"], 2)],
      [("expected a fresh list", ["[2]"], "Default values are evaluated once when the function is defined, so the same list is reused across calls.")],
      "Output: `[1]` then `[1, 2]`. The default `acc=[]` is evaluated once at definition time, so both calls append to the same list. Use `acc=None` and create a new list inside."),
    Q("code_tracing", "intermediate", "python", "Comprehension with a filter",
      """x = [i * i for i in range(5) if i % 2]
print(x)""",
      "What is printed? Explain the filter condition.",
      [("prints [1, 9]", ["[1, 9]", "[1,9]"], 2), ("keeps odd i because i % 2 is truthy", ["odd", "truthy", "non-zero", "nonzero"], 1)],
      [("thought it keeps evens", ["[0, 4, 16]", "[0,4,16]"], "`if i % 2` is truthy when the remainder is 1, i.e. for odd i (1 and 3).")],
      "It prints `[1, 9]`. range(5) yields 0..4; `i % 2` is 1 (truthy) only for odd i = 1, 3, whose squares are 1 and 9."),
    Q("code_tracing", "intermediate", "javascript", "var in a loop with setTimeout",
      """for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}""",
      "What gets logged and why? How would `let` change it?",
      [("logs 3 three times", ["3 3 3", "3, 3, 3", "three 3s", "3 three times", "logs 3", "prints 3"], 2),
       ("var is function-scoped (one shared binding)", ["var", "function-scoped", "function scope", "shared binding", "single binding", "one variable"], 1),
       ("callbacks run after the loop finishes", ["after the loop", "event loop", "asynchron", "callback queue", "later"], 1)],
      [("expected 0 1 2 with var", ["logs 0 1 2", "prints 0 1 2", "logs 0, 1, 2", "prints 0, 1, 2"], "With `var` there is one `i` shared by all callbacks; by the time they run the loop has finished and i is 3.")],
      "It logs 3, 3, 3. `var i` is function-scoped, so all three callbacks close over the same variable, and they run after the loop has finished (i === 3). With `let`, each iteration gets a fresh binding and you'd see 0, 1, 2."),
    Q("code_tracing", "intermediate", "javascript", "Default sort and coercion",
      """console.log([10, 1, 3].sort());
console.log("5" + 3, "5" - 3);""",
      "Predict both lines exactly and explain the surprising parts.",
      [("sort gives [1, 10, 3]", ["[1, 10, 3]", "[1,10,3]"], 2), ("default sort compares strings", ["string", "lexicograph", "unicode", "utf-16", "alphabetical"], 1),
       ("'53' and 2", ["53"], 1), ("+ concatenates, - converts to number", ["coerc", "concaten", "convert"], 1)],
      [("expected numeric sort", ["[1, 3, 10]", "[1,3,10]"], "Without a comparator, sort converts elements to strings and compares them lexicographically, so '10' < '3'.")],
      "Line 1: `[1, 10, 3]` because default sort compares string forms ('1' < '10' < '3'). Line 2: `53 2` — `+` with a string concatenates, while `-` coerces '5' to a number."),

    Q("code_tracing", "advanced", "python", "Generators are lazy",
      """def gen():
    for i in range(3):
        yield i
        print("after", i)

g = gen()
print(next(g))
print(next(g))""",
      "Write the exact output in order and explain what the generator does between calls.",
      [("output is 0, after 0, 1", ["after 0"], 2), ("generator pauses at yield and resumes", ["resume", "pause", "lazy", "suspend", "picks up"], 2),
       ("'after 1' is never printed", ["after 1 is not", "never prints after 1", "not printed", "doesn't print after 1", "does not print after 1", "no after 1"], 1)],
      [("thought the generator runs eagerly", ["after 2", "prints all"], "Generators run lazily; code after a `yield` only runs when the next value is requested.")],
      "Output: `0`, `after 0`, `1`. The first next() runs until the first yield (0). The second next() resumes after the yield, prints 'after 0', loops, and pauses at yield 1. 'after 1' never runs because nobody asks for a third value."),
    Q("code_tracing", "advanced", "python", "Class vs instance attributes",
      """class Counter:
    count = 0
    def __init__(self):
        self.count += 1

a = Counter(); b = Counter()
print(a.count, b.count, Counter.count)""",
      "What is printed? Explain precisely what `self.count += 1` does.",
      [("prints 1 1 0", ["1 1 0", "1, 1, 0"], 2),
       ("creates an instance attribute that shadows the class attribute", ["shadow", "instance attribute", "creates an instance", "new attribute on the instance", "own attribute"], 2)],
      [("thought the class counter is shared and incremented", ["1 2 2", "2 2 2", "1, 2, 2", "2, 2, 2"], "`self.count += 1` reads the class value 0, then assigns 1 to a new instance attribute; Counter.count stays 0.")],
      "It prints `1 1 0`. `self.count += 1` reads Counter.count (0) via attribute lookup, then assigns self.count = 1 on the instance, shadowing the class attribute. The class attribute is never modified."),
    Q("code_tracing", "advanced", "javascript", "Microtasks vs macrotasks",
      """console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
console.log("D");""",
      "Give the exact log order and explain it in terms of the event loop.",
      [("order A D C B", ["a d c b", "a, d, c, b", "a → d → c → b", "a->d->c->b", "adcb"], 2),
       ("promise callbacks are microtasks that run first", ["microtask"], 2), ("setTimeout is a macrotask/timer task", ["macrotask", "task queue", "timer queue", "timers"], 1)],
      [("thought timeout 0 runs before promises", ["a d b c", "a, d, b, c"], "Microtasks (promise reactions) are drained before the next macrotask such as a timer callback.")],
      "A, D, C, B. Synchronous code logs A and D. Then the microtask queue (promise .then) runs C before the event loop picks the next macrotask (the setTimeout callback) which logs B."),
    Q("code_tracing", "advanced", "javascript", "What await really does",
      """async function f() {
  console.log(1);
  await null;
  console.log(2);
}
f();
console.log(3);""",
      "What is the output order? Explain where execution pauses and resumes.",
      [("order 1 3 2", ["1 3 2", "1, 3, 2", "1 → 3 → 2"], 2), ("await suspends and resumes in a microtask", ["await", "microtask", "suspend", "pause", "yield"], 1),
       ("code before the first await runs synchronously", ["synchronous", "immediately", "sync"], 1)],
      [("thought await on a non-promise doesn't pause", ["1 2 3", "1, 2, 3"], "`await` always yields to the caller, even for non-promise values; the rest of f runs in a microtask.")],
      "Output: 1, 3, 2. Calling f() runs synchronously until the first await (logs 1), then returns a pending promise. The caller logs 3. The continuation after `await null` runs as a microtask and logs 2."),

    # ── Debugging ────────────────────────────────────────────────────────────
    Q("debugging", "beginner", "python", "Last n items",
      '''def last_n(items, n):
    """Return the last n items."""
    return items[len(items) - n - 1:]''',
      "This returns the wrong result. Find the bug, explain it, and fix it.",
      [("off-by-one: returns n + 1 items", ["off-by-one", "off by one", "one extra", "n + 1", "n+1", "one too many"], 2),
       ("fix: items[-n:] or remove the -1", ["items[-n:]", "len(items) - n:]", "len(items)-n:]", "remove the - 1", "remove the -1", "remove -1", "drop the -1"], 2),
       ("n = 0 edge case with [-n:]", ["n = 0", "n=0", "n == 0", "zero"], 1)],
      [],
      "The start index has an extra `- 1`, so it returns n + 1 items (off-by-one). Use `items[len(items) - n:]`. Note `items[-n:]` looks nicer but returns the whole list when n == 0."),
    Q("debugging", "beginner", "python", "Find the maximum",
      """def find_max(nums):
    best = 0
    for n in nums:
        if n > best:
            best = n
    return best""",
      "Which inputs give a wrong answer? Explain the root cause and a fix.",
      [("fails when all numbers are negative", ["negative", "below zero", "less than 0", "less than zero"], 2),
       ("initialise from the first element / -inf / use max()", ["nums[0]", "first element", "-inf", "float('-inf')", "max("], 2),
       ("empty list behaviour", ["empty"], 1)],
      [],
      "`best = 0` is a hidden assumption that some number is ≥ 0. For all-negative input like [-5, -2] it returns 0. Initialise with nums[0] (after checking for an empty list) or use max(nums) and decide what an empty list should do."),
    Q("debugging", "beginner", "javascript", "Assignment in a condition",
      """function isAdult(age) {
  if (age = 18) {
    return true;
  }
  return age > 18;
}""",
      "isAdult(5) returns true. Why? Fix it.",
      [("uses assignment instead of comparison", ["assignment", "= instead of", "single =", "assigns"], 2),
       ("18 is truthy, so it always returns true", ["always true", "always returns true", "truthy"], 1), ("fix with >= / ===", [">= 18", "age >= 18", "==="], 2)],
      [],
      "`age = 18` assigns 18 and evaluates to 18, which is truthy, so the function always returns true. Replace the whole body with `return age >= 18;`."),
    Q("debugging", "beginner", "javascript", "Totals from strings",
      """const prices = ["10", "5", "20"];
let total = 0;
for (const p of prices) {
  total = total + p;
}
console.log(total); // expected 35""",
      "What is actually logged, why, and how do you fix it?",
      [("logs '010520'", ["010520"], 1), ("string concatenation instead of addition", ["concaten", "string"], 2),
       ("convert with Number()/parseFloat/unary +", ["number(", "parseint", "parsefloat", "unary +", "+p", "parse"], 2)],
      [],
      "It logs \"010520\" because `+` with a string operand concatenates. Convert first: `total += Number(p)` (or parseFloat), ideally validating that conversion didn't produce NaN."),

    Q("debugging", "intermediate", "python", "Removing while iterating",
      """def remove_evens(nums):
    for n in nums:
        if n % 2 == 0:
            nums.remove(n)
    return nums

print(remove_evens([2, 4, 6, 7]))""",
      "What does this print and why is it wrong? Propose a robust fix.",
      [("mutating a list while iterating skips elements", ["while iterating", "during iteration", "modifying the list", "mutat", "skip", "shifts"], 2),
       ("prints [4, 7]", ["[4, 7]", "[4,7]"], 1), ("build a new list / iterate a copy", ["comprehension", "nums[:]", "copy", "new list", "filter"], 2)],
      [],
      "It prints [4, 7]. Removing items shifts later elements left while the iterator index keeps advancing, so 4 is skipped. Build a new list: `return [n for n in nums if n % 2]` (or iterate over a copy)."),
    Q("debugging", "intermediate", "python", "Leaking a file handle",
      """import json

def load_config(path):
    f = open(path)
    data = json.load(f)
    if "debug" not in data:
        raise ValueError("missing debug")
    f.close()
    return data""",
      "Find the resource bug and fix it idiomatically.",
      [("file is not closed when an exception is raised", ["leak", "not closed", "never closed", "exception", "raise"], 2),
       ("use a with-block / context manager (or finally)", ["with open", "context manager", "finally"], 2)],
      [],
      "If json.load fails or the ValueError is raised, f.close() never runs and the handle leaks. Use `with open(path) as f: data = json.load(f)` so the file is closed on every path."),
    Q("debugging", "intermediate", "javascript", "forEach with async",
      """async function loadAll(ids) {
  const results = [];
  ids.forEach(async (id) => {
    const r = await fetchItem(id);
    results.push(r);
  });
  return results;
}""",
      "Callers always get an empty array. Explain why and fix it.",
      [("forEach does not await async callbacks", ["foreach", "does not wait", "doesn't wait", "not awaited", "doesn't await", "does not await", "fire and forget"], 2),
       ("returns before any fetch completes (empty array)", ["empty", "before"], 1), ("use Promise.all with map, or for...of with await", ["promise.all", "for...of", "for of", "for (const"], 2)],
      [],
      "forEach ignores the promises returned by the async callback, so loadAll returns `results` before any fetch finishes. Use `return Promise.all(ids.map(fetchItem))` (parallel) or a `for...of` loop with `await` (sequential)."),
    Q("debugging", "intermediate", "javascript", "Crash on some users",
      """function getUserName(user) {
  return user.profile.name || "Anonymous";
}
// Crashes for some users in production""",
      "What crashes, for which users, and how would you fix it?",
      [("profile can be undefined/null", ["undefined", "null", "missing profile", "no profile"], 2), ("TypeError: cannot read properties of undefined", ["typeerror", "cannot read"], 1),
       ("optional chaining / nullish coalescing", ["?.", "optional chaining", "??"], 2)],
      [],
      "Users without a profile make `user.profile` undefined, and reading `.name` throws a TypeError. Use `user?.profile?.name ?? \"Anonymous\"` (?? also keeps legitimate falsy values differently from ||)."),

    Q("debugging", "advanced", "python", "Lost increments with threads",
      """import threading

counter = 0

def work():
    global counter
    for _ in range(100_000):
        counter += 1

threads = [threading.Thread(target=work) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # sometimes less than 400000""",
      "Explain the root cause and fix it.",
      [("race condition", ["race"], 2), ("+= is not atomic (read-modify-write interleaving)", ["atomic", "read-modify-write", "interleav", "read, add", "not thread-safe", "not thread safe"], 2),
       ("protect with a Lock (or avoid shared state)", ["lock"], 2)],
      [("blames the GIL as a guarantee", ["gil prevents", "gil makes it safe"], "The GIL does not make `counter += 1` atomic; a thread can be switched between the read and the write.")],
      "`counter += 1` is a read-modify-write sequence; threads can interleave between the read and write, losing updates (a race condition). Guard it with a `threading.Lock()` or have each thread compute a local sum and combine results."),
    Q("debugging", "advanced", "python", "Late-binding closures",
      """handlers = [lambda: i for i in range(3)]
print([h() for h in handlers])  # expected [0, 1, 2]""",
      "What is printed instead, why, and how do you fix it?",
      [("prints [2, 2, 2]", ["[2, 2, 2]", "[2,2,2]"], 2), ("closures look up i when called (late binding)", ["late binding", "looked up", "when called", "closure", "by reference", "same variable"], 2),
       ("bind the value: default argument or functools.partial", ["i=i", "default argument", "partial"], 2)],
      [],
      "It prints [2, 2, 2]. Each lambda closes over the variable i, not its value at creation; when called, i is 2. Bind early: `lambda i=i: i` or functools.partial."),
    Q("debugging", "advanced", "javascript", "A memoize that forgets",
      """function memoize(fn) {
  const cache = {};
  return (arg) => {
    if (cache[arg]) return cache[arg];
    return (cache[arg] = fn(arg));
  };
}""",
      "Find the subtle bugs in this memoize and fix them.",
      [("falsy results (0, '', false) are never cached", ["falsy", "0", "false", "empty string"], 2),
       ("use `in` / Map.has / !== undefined", ["has(", "in cache", "map", "hasownproperty", "!== undefined"], 2),
       ("object keys coerce args to strings (1 vs '1', objects)", ["string key", "coerc", "[object object]", "tostring"], 1)],
      [],
      "`if (cache[arg])` treats cached falsy results (0, '', false, null) as misses, so fn re-runs. Also plain-object keys stringify args, so 1 and '1' collide and objects all become '[object Object]'. Use a Map and `cache.has(arg)`."),
    Q("debugging", "advanced", "javascript", "Sorting by age",
      """function sortByAge(users) {
  return users.sort((a, b) => a.age > b.age);
}""",
      "Why does this sort behave inconsistently, and what else is risky here?",
      [("comparator must return a number (neg/0/pos), not a boolean", ["negative", "number", "a.age - b.age", "boolean"], 2),
       ("sort mutates the caller's array in place", ["mutat", "in place", "in-place", "original array"], 2), ("copy first ([...users] / slice / toSorted)", ["[...users]", "slice()", "tosorted"], 1)],
      [],
      "The comparator returns true/false (1/0), never a negative number, so the sort algorithm gets inconsistent answers. Use `(a, b) => a.age - b.age`. Also `.sort` mutates the input array; use `[...users].sort(...)` or `users.toSorted(...)`."),

    # ── Algorithmic thinking ─────────────────────────────────────────────────
    Q("algorithmic_thinking", "beginner", "python", "Linear search cost",
      """def contains(items, target):
    for x in items:
        if x == target:
            return True
    return False""",
      "What is the time complexity (best and worst case)? How could lookups be made faster if this is called many times?",
      [("O(n) worst case", ["o(n)", "linear"], 2), ("worst case is when the target is absent or last", ["worst", "not present", "absent", "last"], 1),
       ("use a set for O(1) average lookups", ["set", "hash", "o(1)"], 2)],
      [],
      "Worst case O(n) (target missing or last), best case O(1) (first element), O(1) extra space. For repeated lookups, build a set once (O(n)) and then each membership test is O(1) on average."),
    Q("algorithmic_thinking", "beginner", "python", "Duplicate check",
      """def has_duplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False""",
      "What is the complexity? Propose a faster approach and its tradeoff.",
      [("O(n^2) time", ["o(n^2)", "o(n²)", "quadratic", "n squared", "n*n"], 2), ("use a set: O(n) time", ["set", "hash"], 2),
       ("tradeoff: O(n) extra memory", ["memory", "space"], 1)],
      [],
      "Nested loops compare every pair: O(n²) time, O(1) space. Track seen values in a set (or compare len(set(nums)) with len(nums)) for O(n) time at the cost of O(n) extra memory."),
    Q("algorithmic_thinking", "beginner", "javascript", "Sum to n",
      """function sumTo(n) {
  let s = 0;
  for (let i = 1; i <= n; i++) s += i;
  return s;
}""",
      "State the complexity and describe a constant-time alternative.",
      [("O(n)", ["o(n)", "linear"], 2), ("closed form n(n+1)/2", ["n * (n + 1) / 2", "n(n+1)/2", "n*(n+1)/2", "gauss", "formula"], 2), ("O(1)", ["o(1)", "constant"], 1)],
      [],
      "The loop is O(n). Gauss's formula n·(n+1)/2 computes the same value in O(1) (watch for overflow/precision beyond Number.MAX_SAFE_INTEGER)."),
    Q("algorithmic_thinking", "beginner", "javascript", "Hot-path membership",
      """const names = ["ana", "bo", "cy" /* ...10,000 names */];
function isRegistered(name) {
  return names.includes(name);
}
// called thousands of times per second""",
      "What does each call cost, and how would you make it cheaper?",
      [("includes scans linearly: O(n)", ["o(n)", "linear", "scan"], 2), ("use a Set", ["set"], 2), ("Set.has is O(1) on average", ["o(1)", "constant"], 1)],
      [],
      "Array.includes is a linear scan, O(n) per call (~10k comparisons). Build `const registered = new Set(names)` once and use `registered.has(name)`, which is O(1) on average."),

    Q("algorithmic_thinking", "intermediate", "python", "Binary search",
      """def find(sorted_nums, target):
    lo, hi = 0, len(sorted_nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        if sorted_nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1""",
      "What is the complexity and why? What precondition must hold?",
      [("O(log n)", ["o(log n)", "logarithmic", "log n", "log(n)"], 2), ("halves the search range each step", ["half", "halv"], 1), ("input must be sorted", ["sorted"], 2)],
      [],
      "O(log n) time, O(1) space: each iteration halves the remaining range. It only works if the input is sorted ascending; otherwise discarding half the range is unjustified."),
    Q("algorithmic_thinking", "intermediate", "python", "Naive Fibonacci",
      """def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)""",
      "Why is fib(40) slow? Analyse the complexity and improve it.",
      [("exponential time", ["exponential", "o(2^n)", "2^n", "o(1.6", "phi"], 2), ("recomputes overlapping subproblems", ["repeat", "overlapping", "recomput", "same subproblem", "again and again"], 2),
       ("memoize / DP / iterative → O(n)", ["memo", "lru_cache", "dynamic programming", "bottom-up", "iterative", "o(n)"], 2)],
      [],
      "Each call branches into two, recomputing the same subproblems, giving ~O(φⁿ) ≈ O(1.6ⁿ) (often written O(2ⁿ)). Memoize (functools.lru_cache) or iterate with two variables for O(n) time and O(1) space."),
    Q("algorithmic_thinking", "intermediate", "javascript", "Two-sum",
      """function twoSum(nums, target) {
  for (let i = 0; i < nums.length; i++)
    for (let j = i + 1; j < nums.length; j++)
      if (nums[i] + nums[j] === target) return [i, j];
  return null;
}""",
      "Analyse the complexity and design a faster algorithm.",
      [("O(n^2) currently", ["o(n^2)", "o(n²)", "quadratic"], 1), ("store seen values in a hash map and look up the complement", ["map", "complement", "target - "], 2),
       ("O(n) single pass", ["o(n)", "linear", "single pass", "one pass"], 2)],
      [],
      "Brute force is O(n²). In one pass, keep a Map value→index; for each x check whether target − x is already in the map. That's O(n) time and O(n) space."),
    Q("algorithmic_thinking", "intermediate", "javascript", "Queue with shift()",
      """function processQueue(queue) {
  while (queue.length > 0) {
    const job = queue.shift();
    run(job);
  }
}
// queue can hold 1,000,000 jobs""",
      "Why might this be slow for large queues? How would you fix it?",
      [("shift() is O(n) (re-indexes the array)", ["shift", "re-index", "reindex", "moves every element", "o(n)"], 2), ("overall O(n^2)", ["o(n^2)", "o(n²)", "quadratic"], 2),
       ("use a head index / proper deque / iterate", ["index", "pointer", "pop", "deque", "linked list", "head", "for...of"], 1)],
      [],
      "Array.shift removes the first element and shifts the rest, O(n) each, so draining n jobs is O(n²). Iterate with an index (`for (let i = 0; ...)`), or use a real queue/deque with a head pointer."),

    Q("algorithmic_thinking", "advanced", "python", "Top-k of a huge list",
      """def top_k(nums, k):
    return sorted(nums, reverse=True)[:k]

# nums has 10 million items, k = 10""",
      "Analyse the cost and propose a better algorithm for small k.",
      [("sorting is O(n log n)", ["n log n", "nlogn", "n*log(n)"], 2), ("use a heap (heapq.nlargest)", ["heap", "heapq", "nlargest"], 2), ("O(n log k)", ["n log k", "log k"], 2)],
      [],
      "Sorting is O(n log n) and copies the list. A size-k min-heap (heapq.nlargest(k, nums)) is O(n log k) time and O(k) extra space — much better when k ≪ n. Quickselect gives O(n) average."),
    Q("algorithmic_thinking", "advanced", "python", "Pairs with difference d",
      """def count_pairs_with_diff(nums, d):
    nums.sort()
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[j] - nums[i] == d:
                count += 1
            elif nums[j] - nums[i] > d:
                break
    return count""",
      "Is this O(n log n)? Analyse best/worst cases and propose an approach with better guarantees.",
      [("sort is O(n log n)", ["n log n"], 1), ("worst case still quadratic", ["o(n^2)", "o(n²)", "quadratic", "worst case"], 2),
       ("duplicates / d = 0 / large d trigger the worst case", ["duplicate", "d = 0", "d=0", "equal", "large d"], 1), ("Counter/hash map or two pointers", ["counter", "hash", "dictionary", "two pointer", "two-pointer"], 2)],
      [],
      "The break helps, but with many equal values (d = 0) or a large d the inner loop still scans far: worst case O(n²). Use a Counter: for each value v add count[v + d] (handle d = 0 as C(c,2) per value) for O(n) after counting; it also avoids mutating the input with sort()."),
    Q("algorithmic_thinking", "advanced", "javascript", "canSum never finishes",
      """function canSum(target, nums) {
  if (target === 0) return true;
  if (target < 0) return false;
  return nums.some((n) => canSum(target - n, nums));
}
// canSum(300, [7, 14]) never finishes""",
      "Why does this explode? Analyse it and make it efficient.",
      [("exponential branching", ["exponential", "o(m^", "o(n^", "branch"], 2), ("memoize on target / DP", ["memo", "cache", "dynamic programming", "dp"], 2),
       ("O(target × nums) after memoization", ["target * ", "target ×", "t * m", "t*m", "m * t", "o(t"], 1),
       ("300 is unreachable so every branch is explored", ["multiple of 7", "never reaches 0", "not divisible", "unreachable", "every branch"], 1)],
      [],
      "Each call branches m ways and depth is up to target/min(nums), so time is O(m^(target/min)). 300 isn't a multiple of 7, so no branch succeeds and `some` must explore everything. Memoize results per target (Map) or use a bottom-up boolean DP: O(target × m)."),
    Q("algorithmic_thinking", "advanced", "javascript", "Shortest path with a stack",
      """function shortestPath(graph, start, goal) {
  // graph: adjacency list, unweighted
  const stack = [[start, 0]];
  const seen = new Set([start]);
  while (stack.length) {
    const [node, dist] = stack.pop();
    if (node === goal) return dist;
    for (const next of graph[node]) {
      if (!seen.has(next)) { seen.add(next); stack.push([next, dist + 1]); }
    }
  }
  return -1;
}""",
      "Does this always return the shortest distance? Explain and fix; state the complexity.",
      [("stack makes it DFS, which doesn't guarantee shortest paths", ["dfs", "depth-first", "depth first", "stack"], 2), ("use BFS with a queue", ["bfs", "breadth", "queue"], 2),
       ("O(V + E)", ["v + e", "v+e"], 1)],
      [],
      "Popping from a stack explores depth-first, and marking nodes seen on push can lock in a longer path. Use BFS (FIFO queue): in an unweighted graph the first time you dequeue the goal its distance is minimal. Time O(V + E), space O(V)."),
]
