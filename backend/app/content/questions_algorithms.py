"""Seed questions: Algorithms (approach, correctness, complexity) — Python, JavaScript, PHP and prose."""

from app.content.qdef import Q

D = "algorithms"

QUESTIONS_ALGORITHMS = [
    # ── Beginner ────────────────────────────────────────────────────────────
    Q(D, "beginner", "python", "Searching a sorted list",
      """def find(items, target):        # items is sorted, called 100,000 times
    for i, x in enumerate(items):
        if x == target:
            return i
    return -1""",
      "Explain the current approach and its cost, then the algorithm you would use instead and why it is correct.",
      [("use binary search because the list is sorted", ["binary search", "bisect"], 2),
       ("O(n) per lookup now, O(log n) with binary search", ["o(log n)", "log n"], 1),
       ("returns the first match or -1", ["first", "-1"], 0.5)],
      [],
      "It is a linear scan: O(n) per lookup, returning the first index or -1. Because items is sorted, use binary "
      "search (bisect_left): each comparison discards half the remaining range, so each lookup is O(log n)."),
    Q(D, "beginner", "python", "Two pointers on a sorted array",
      """def has_pair(nums, target):     # nums sorted ascending
    i, j = 0, len(nums) - 1
    while i < j:
        s = nums[i] + nums[j]
        if s == target:
            return True
        if s < target:
            i += 1
        else:
            j -= 1
    return False""",
      "Why is it safe to move i forward when the sum is too small? Give the time and space complexity.",
      [("sorted order makes discarding safe", ["sorted", "too small", "cannot pair", "can't pair", "discard", "safely"], 2),
       ("O(n) time", ["o(n)", "linear"], 1), ("O(1) extra space", ["o(1)", "constant space"], 1)],
      [],
      "Because nums is sorted, if nums[i] + nums[j] is too small then nums[i] plus any element at or before j is "
      "also too small, so nums[i] can be discarded safely (symmetrically for j). Each step discards one element: "
      "O(n) time, O(1) extra space."),
    Q(D, "beginner", "python", "Bubble sort with early exit",
      """def bubble(a):
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a""",
      "Give best- and worst-case complexity and the invariant that makes it correct.",
      [("worst case O(n^2)", ["o(n^2)", "o(n²)", "quadratic"], 2),
       ("best case O(n) on sorted input thanks to the early exit", ["o(n)", "already sorted", "early exit", "best case"], 1),
       ("after pass i the largest elements are in place at the end", ["largest", "in place", "end"], 1)],
      [],
      "Worst/average case O(n^2). Best case O(n): on already sorted input the first pass makes no swaps and the "
      "early exit stops. Invariant: after pass i the largest i+1 elements are in their final place at the end."),
    Q(D, "beginner", "javascript", "First unique character",
      """function firstUnique(s) {
  const count = new Map();
  for (const ch of s) count.set(ch, (count.get(ch) || 0) + 1);
  for (let i = 0; i < s.length; i++) {
    if (count.get(s[i]) === 1) return i;
  }
  return -1;
}""",
      "Explain the approach and its time and space complexity.",
      [("two passes: count frequencies, then find the first count of 1", ["count", "frequenc", "two pass", "second pass"], 2),
       ("O(n) time", ["o(n)", "linear"], 1), ("O(k) space for distinct characters", ["space", "o(k)", "distinct", "alphabet"], 1)],
      [],
      "First pass counts each character's frequency in a Map; second pass returns the first index whose count is 1. "
      "O(n) time and O(k) space for k distinct characters. (Caveat: for…of iterates code points while s[i] uses "
      "UTF-16 units, so astral emoji need care.)"),
    Q(D, "beginner", "javascript", "Recursive digit sum",
      """function digitSum(n) {
  if (n < 10) return n;
  return (n % 10) + digitSum(Math.floor(n / 10));
}""",
      "Explain the base case, why it is correct, its complexity, and an input it gets wrong.",
      [("base case: a single digit returns itself", ["base case", "single digit", "n < 10"], 2),
       ("O(number of digits) = O(log n) calls", ["log n", "digits", "o(d)"], 1),
       ("negative input is returned unchanged (bug)", ["negative"], 1)],
      [],
      "Base case: n < 10 is a single digit and returns itself. Otherwise it adds the last digit (n % 10) to the "
      "digit sum of the rest, shrinking n by one digit per call: O(d) = O(log n) calls. A negative input is "
      "returned unchanged because -123 < 10."),
    Q(D, "beginner", "php", "Maximum in one pass",
      """<?php
function maxOf(array $xs) {
    $best = $xs[0];
    foreach ($xs as $x) {
        if ($x > $best) $best = $x;
    }
    return $best;
}""",
      "Argue correctness with an invariant, give the complexity, and name an edge case.",
      [("invariant: best is the maximum of the elements seen so far", ["so far", "seen", "invariant"], 2),
       ("O(n), one pass", ["o(n)", "linear", "one pass", "single pass"], 1),
       ("empty array edge case", ["empty"], 1)],
      [],
      "Invariant: after each iteration $best is the maximum of the elements seen so far, so after the loop it is the "
      "overall max. One pass: O(n). Edge case: an empty array reads $xs[0], which emits a warning and returns null; "
      "also arrays whose keys don't start at 0."),
    Q(D, "beginner", "php", "Binary search loop",
      """<?php
function bsearch(array $a, int $t): int {
    $lo = 0; $hi = count($a) - 1;
    while ($lo <= $hi) {
        $mid = intdiv($lo + $hi, 2);
        if ($a[$mid] === $t) return $mid;
        if ($a[$mid] < $t) $lo = $mid + 1; else $hi = $mid - 1;
    }
    return -1;
}""",
      "Why does it terminate, what is its complexity, and what precondition does it need?",
      [("the range halves each step: O(log n)", ["o(log n)", "log n", "halves", "half"], 2),
       ("terminates because lo rises or hi falls every iteration", ["terminat", "shrink", "lo > hi"], 1),
       ("the array must be sorted", ["sorted"], 1)],
      [],
      "Each iteration either returns or moves lo up / hi down past mid, so the range shrinks and the loop "
      "terminates when lo > hi. The range halves each step, giving O(log n). Precondition: $a is sorted (and a "
      "list with keys 0..n-1)."),
    Q(D, "beginner", "general", "Greedy change-making",
      """Coins: 1, 5, 10, 25
Amount: 63
Greedy: always take the largest coin that fits.""",
      "Which coins does greedy pick? Is greedy always optimal for change-making?",
      [("6 coins: 25, 25, 10, 1, 1, 1", ["6 coins", "six coins", "25, 25, 10"], 2),
       ("greedy is optimal for this canonical coin system", ["canonical", "optimal"], 1),
       ("not for every system (counterexample)", ["counterexample", "not always", "doesn't always", "does not always", "1, 3, 4"], 1)],
      [],
      "Greedy picks 25, 25, 10, 1, 1, 1 — 6 coins, which is optimal for this canonical (US-style) system. It is not "
      "always optimal: with coins 1, 3, 4 and amount 6 greedy gives 4+1+1 (3 coins) but 3+3 uses 2 — a counterexample."),
    Q(D, "beginner", "general", "Shortest path in a grid",
      """S . . #
# # . #
. . . E
S = start, E = end, # = wall. Moves: up, down, left, right.""",
      "What is the minimum number of moves, and which algorithm guarantees it?",
      [("5 moves", ["5", "five"], 2), ("BFS explores in layers of distance", ["bfs", "breadth", "layer", "level"], 1)],
      [],
      "5 moves: right, right, down, down, right. BFS (breadth-first search) explores cells in layers of increasing "
      "distance, so the first time it reaches E is a shortest path in an unweighted grid."),

    # ── Intermediate ────────────────────────────────────────────────────────
    Q(D, "intermediate", "python", "Sliding window sum",
      """def max_window(nums, k):
    s = sum(nums[:k])
    best = s
    for i in range(k, len(nums)):
        s += nums[i] - nums[i - k]
        best = max(best, s)
    return best""",
      "Explain how the window is maintained, compare with the naive approach, and name edge cases.",
      [("add the incoming element, subtract the outgoing one", ["subtract", "outgoing", "leaving", "incoming", "drops"], 2),
       ("O(n) instead of O(n·k)", ["o(n)", "linear"], 1), ("edge cases: k > len, k = 0, empty", ["k > len", "edge", "empty", "k = 0"], 1)],
      [],
      "The window sum is updated in O(1) per step: add the incoming nums[i] and subtract the outgoing nums[i-k]. "
      "Total O(n) instead of O(n·k) for re-summing each window. Edge cases: empty input, k = 0 or k > len(nums)."),
    Q(D, "intermediate", "python", "Merging two sorted lists",
      """def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return out + a[i:] + b[j:]""",
      "Why `<=` rather than `<`? Why append the slices at the end? What does this give merge sort overall?",
      [("<= keeps equal elements in order (stable)", ["stable", "stability"], 2),
       ("the leftover tail is already sorted", ["remaining", "leftover", "rest"], 1),
       ("O(n) merge, O(n log n) merge sort", ["n log n", "o(n)"], 1)],
      [],
      "Using <= takes from a first on ties, which keeps equal elements in original order — merge sort stays stable. "
      "When one list runs out, the remaining tail of the other is already sorted and can be appended. The merge is "
      "O(n), so merge sort is O(n log n)."),
    Q(D, "intermediate", "python", "Climbing stairs",
      """def ways(n):        # steps of size 1 or 2
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a""",
      "Derive the recurrence, give ways(4), and the complexity.",
      [("f(n) = f(n−1) + f(n−2) by the last step", ["f(n-1)", "n-1", "fibonacci", "last step"], 2),
       ("O(n) time, O(1) space", ["o(n)", "o(1)"], 1), ("ways(4) = 5", ["5"], 0.5)],
      [],
      "The last step is 1 or 2, so f(n) = f(n-1) + f(n-2) with f(0) = f(1) = 1 — the Fibonacci numbers. ways(4) = 5. "
      "Keeping only two values gives O(n) time and O(1) space."),
    Q(D, "intermediate", "javascript", "Cycle detection with DFS colors",
      """function hasCycle(graph) {            // { node: [neighbors] }
  const state = {};                   // undefined | 1 (on stack) | 2 (done)
  const dfs = (u) => {
    state[u] = 1;
    for (const v of graph[u] || []) {
      if (state[v] === 1) return true;
      if (!state[v] && dfs(v)) return true;
    }
    state[u] = 2;
    return false;
  };
  return Object.keys(graph).some((u) => !state[u] && dfs(u));
}""",
      "Why does reaching a node with state 1 mean a cycle but state 2 does not? Give the complexity.",
      [("an edge to a node still on the recursion stack is a back edge", ["back edge", "on the stack", "recursion stack", "in stack", "state 1"], 2),
       ("finished (state 2) nodes are cross/forward edges, not cycles", ["finished", "done", "state 2", "cross"], 1),
       ("O(V + E)", ["o(v + e)", "o(v+e)", "v + e"], 1)],
      [],
      "State 1 means the node is on the current recursion stack, so an edge to it is a back edge that closes a cycle. "
      "State 2 nodes are finished: reaching one is a cross/forward edge, no cycle through the current path. Each node "
      "and edge is processed once: O(V + E)."),
    Q(D, "intermediate", "javascript", "Interval scheduling",
      """function maxMeetings(meetings) {     // [start, end]
  meetings.sort((a, b) => a[1] - b[1]);
  let count = 0, lastEnd = -Infinity;
  for (const [s, e] of meetings) {
    if (s >= lastEnd) { count++; lastEnd = e; }
  }
  return count;
}""",
      "Why sort by end time? Prove the greedy choice is safe and give the complexity.",
      [("earliest end leaves the most room (exchange argument)", ["earliest end", "finishes first", "exchange", "most room"], 2),
       ("O(n log n) for sorting", ["n log n"], 1), ("sorting by start time fails", ["start time", "long meeting", "counterexample"], 0.5)],
      [],
      "Picking the meeting that finishes first leaves the most room for the rest. Exchange argument: in any optimal "
      "schedule, swap its first meeting for the earliest-ending one without conflicts. Sorting dominates: O(n log n). "
      "Sorting by start time fails when one long meeting starts first."),
    Q(D, "intermediate", "php", "Two-sum with a hash map",
      """<?php
function twoSum(array $nums, int $target): ?array {
    $seen = [];
    foreach ($nums as $i => $n) {
        $need = $target - $n;
        if (isset($seen[$need])) return [$seen[$need], $i];
        $seen[$n] = $i;
    }
    return null;
}""",
      "Explain the approach, why the lookup happens before the insert, and the complexity.",
      [("look up the complement in a hash map", ["complement", "hash", "lookup", "$need"], 2),
       ("checking before inserting avoids reusing the same element", ["before", "same element", "same index", "reuse"], 1),
       ("O(n) time and space", ["o(n)", "linear"], 1)],
      [],
      "For each number it looks up the complement (target − n) in a hash map of earlier values → index. Checking "
      "before inserting avoids pairing an element with itself (same index). One pass: O(n) time, O(n) space."),
    Q(D, "intermediate", "php", "K-th smallest element",
      """<?php
function kthSmallest(array $a, int $k): int {
    sort($a);
    return $a[$k - 1];
}""",
      "What is the complexity, and which algorithms do better?",
      [("O(n log n) because of the full sort", ["n log n"], 2),
       ("quickselect: partition, average O(n)", ["quickselect", "partition"], 1),
       ("a heap of size k, or worst-case caveats", ["heap", "worst"], 0.5)],
      [],
      "Sorting makes it O(n log n). Quickselect partitions around a pivot and recurses into one side: average O(n) "
      "(worst O(n^2) without good pivots). A max-heap of size k gives O(n log k)."),
    Q(D, "intermediate", "general", "Build order",
      """build   needs compile
test    needs build
deploy  needs test, lint
lint    needs nothing
compile needs nothing""",
      "Give a valid order, name the algorithm, and say when no order exists.",
      [("a valid topological order", ["compile, lint, build, test, deploy", "compile, build, lint, test, deploy",
                                      "lint, compile, build, test, deploy", "compile, build, test, lint, deploy"], 2),
       ("topological sort (Kahn / in-degree)", ["topological", "kahn", "in-degree", "indegree"], 1),
       ("impossible if there is a cycle", ["cycle"], 1)],
      [],
      "One valid order: compile, lint, build, test, deploy. This is a topological sort, e.g. Kahn's algorithm: "
      "repeatedly take a task with in-degree 0. If a cycle exists, no valid order exists."),
    Q(D, "intermediate", "general", "Weighted roads",
      """Roads (minutes):  A–B 1,  B–C 1,  A–C 5,  C–D 1
Fastest route from A to D?""",
      "What is the fastest time, and why does plain BFS get it wrong?",
      [("3 minutes via A–B–C–D", ["3 minutes", "a-b-c-d", "a–b–c–d", "a→b→c→d"], 2),
       ("BFS minimises the number of edges, not total weight", ["bfs", "fewest edges", "number of edges"], 1),
       ("use Dijkstra with a priority queue", ["dijkstra", "priority queue"], 1)],
      [],
      "3 minutes via A-B-C-D. BFS minimises the number of edges, so it would choose A–C–D (2 edges, 6 minutes). "
      "With non-negative weights use Dijkstra's algorithm with a priority queue."),

    # ── Advanced ────────────────────────────────────────────────────────────
    Q(D, "advanced", "python", "Patience-sorting LIS",
      """from bisect import bisect_left

def lis(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)""",
      "What does tails[i] mean, why is the answer correct, and what is the complexity?",
      [("tails[i] is the smallest possible tail of an increasing subsequence of length i+1", ["smallest tail", "smallest possible", "smallest ending"], 2),
       ("O(n log n) via binary search", ["n log n"], 1),
       ("tails is not the actual subsequence", ["not the actual", "not the subsequence", "isn't the"], 1)],
      [],
      "tails[i] is the smallest possible tail of a strictly increasing subsequence of length i+1; it stays sorted, "
      "so binary search finds where x fits. Replacing keeps tails as small as possible, appending extends the best "
      "length. O(n log n). Note tails is not the actual subsequence, only its length is reliable."),
    Q(D, "advanced", "python", "0/1 knapsack in one array",
      """def knap(items, W):           # items: [(weight, value)]
    dp = [0] * (W + 1)
    for w, v in items:
        for c in range(W, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[W]""",
      "Why must capacity be iterated downward? Give the complexity and its caveat.",
      [("downward iteration uses each item at most once", ["once", "downward", "backward", "reverse", "descending"], 2),
       ("O(n·W), pseudo-polynomial", ["n·w", "n*w", "o(nw)", "pseudo"], 1),
       ("upward would allow reusing items (unbounded knapsack)", ["unbounded", "reuse", "multiple times"], 1)],
      [],
      "Going downward means dp[c - w] still holds the value from before this item, so each item is used at most once "
      "(0/1). Iterating upward would reuse the item multiple times — the unbounded knapsack. O(n·W) time, which is "
      "pseudo-polynomial in the numeric value W."),
    Q(D, "advanced", "python", "Union-Find",
      """parent = list(range(n))

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(a, b):
    parent[find(a)] = find(b)""",
      "What does the line in find do, what is missing for the best bound, and what is that bound?",
      [("path halving (compression) flattens the trees", ["path halving", "path compression", "halving", "compress"], 2),
       ("union by rank or size is missing", ["rank", "size"], 1),
       ("near-constant amortized: inverse Ackermann α(n)", ["ackermann", "α(n)", "alpha", "amortized"], 1)],
      [],
      "parent[x] = parent[parent[x]] is path halving, a form of path compression that flattens the trees. union "
      "lacks union by rank/size. With both, operations take amortized O(α(n)) — inverse Ackermann, effectively "
      "constant."),
    Q(D, "advanced", "javascript", "Edit distance with memo",
      """function edit(a, b, i = 0, j = 0, memo = new Map()) {
  if (i === a.length) return b.length - j;
  if (j === b.length) return a.length - i;
  const key = i + "," + j;
  if (memo.has(key)) return memo.get(key);
  const r = a[i] === b[j]
    ? edit(a, b, i + 1, j + 1, memo)
    : 1 + Math.min(edit(a, b, i + 1, j, memo),      // delete
                   edit(a, b, i, j + 1, memo),      // insert
                   edit(a, b, i + 1, j + 1, memo)); // replace
  memo.set(key, r);
  return r;
}""",
      "Explain the recurrence, the complexity, and a practical limitation.",
      [("three choices: delete, insert, replace", ["delete", "insert", "replace", "substitut"], 2),
       ("O(n·m) distinct subproblems", ["n·m", "n*m", "o(nm)", "o(mn)"], 1),
       ("recursion depth; a bottom-up table avoids it", ["stack", "depth", "bottom-up", "tabulat", "iterative"], 1)],
      [],
      "If characters match, move both indices; otherwise take 1 + the best of delete, insert or replace. There are "
      "O(n·m) distinct (i, j) subproblems, each O(1) with the memo. Recursion depth reaches n + m, so long strings can "
      "overflow the stack — a bottom-up table (tabulation) avoids that."),
    Q(D, "advanced", "javascript", "Kadane's algorithm",
      """function maxSub(a) {
  let best = a[0], cur = a[0];
  for (let i = 1; i < a.length; i++) {
    cur = Math.max(a[i], cur + a[i]);
    best = Math.max(best, cur);
  }
  return best;
}""",
      "What does cur represent, why is the max correct, and how are all-negative arrays handled?",
      [("cur is the best sum of a subarray ending at i", ["ending at", "ends at"], 2),
       ("restart when extending would hurt (negative prefix)", ["restart", "negative", "start fresh", "start over"], 1),
       ("O(n); all-negative returns the largest element", ["o(n)", "all negative", "all-negative"], 1)],
      [],
      "cur is the maximum sum of a subarray ending at i: either extend the previous best or restart at a[i] when the "
      "previous sum is negative. best tracks the max over all end points. O(n), and starting from a[0] handles "
      "all-negative arrays (returns the largest element)."),
    Q(D, "advanced", "javascript", "Backtracking permutations",
      """function perms(xs) {
  const out = [], cur = [], used = Array(xs.length).fill(false);
  (function go() {
    if (cur.length === xs.length) { out.push([...cur]); return; }
    for (let i = 0; i < xs.length; i++) {
      if (used[i]) continue;
      used[i] = true; cur.push(xs[i]);
      go();
      cur.pop(); used[i] = false;
    }
  })();
  return out;
}""",
      "Explain the backtracking pattern, why [...cur] is copied, and the complexity.",
      [("choose, recurse, then undo (backtrack)", ["undo", "backtrack", "unchoose", "pop"], 2),
       ("copy because cur is mutated afterwards", ["copy", "mutat", "same array", "reference"], 1),
       ("O(n · n!)", ["n!", "factorial"], 1)],
      [],
      "Each level chooses an unused element, recurses, then undoes the choice (pop and unmark) — backtracking. "
      "[...cur] is copied because cur is the same array that keeps being mutated. There are n! permutations, each "
      "copied in O(n): O(n · n!). Duplicates in xs yield duplicate permutations."),
    Q(D, "advanced", "php", "Grid paths with walls",
      """<?php
function paths(array $g): int {            // 0 = free, 1 = wall
    $R = count($g); $C = count($g[0]);
    $dp = array_fill(0, $C, 0);
    $dp[0] = $g[0][0] ? 0 : 1;
    for ($r = 0; $r < $R; $r++)
        for ($c = 0; $c < $C; $c++) {
            if ($g[$r][$c]) { $dp[$c] = 0; continue; }
            if ($c > 0) $dp[$c] += $dp[$c - 1];
        }
    return $dp[$C - 1];
}""",
      "State the recurrence (moves: right or down), explain the one-row trick, and give the complexity.",
      [("paths = from above + from the left", ["above", "top", "left"], 2),
       ("a rolling 1D row: dp[c] still holds the row above before the update", ["rolling", "previous row", "one row", "1d"], 1),
       ("O(R·C) time, O(C) space", ["o(r·c)", "o(r*c)", "o(rc)", "o(c)"], 1)],
      [],
      "paths(r, c) = paths from above + paths from the left, and 0 on a wall. Using a rolling 1D row, dp[c] still "
      "holds the value from the row above before it is updated, and dp[c-1] is already the current row. O(R·C) "
      "time and O(C) space."),
    Q(D, "advanced", "php", "Dijkstra with SplPriorityQueue",
      """<?php
function dijkstra(array $adj, $src): array {
    $dist = [$src => 0];
    $pq = new SplPriorityQueue();
    $pq->insert($src, 0);
    while (!$pq->isEmpty()) {
        $u = $pq->extract();
        foreach ($adj[$u] ?? [] as [$v, $w]) {
            $nd = $dist[$u] + $w;
            if (!isset($dist[$v]) || $nd < $dist[$v]) {
                $dist[$v] = $nd;
                $pq->insert($v, -$nd);
            }
        }
    }
    return $dist;
}""",
      "Why is the priority negated? What precondition and complexity apply, and what inefficiency remains?",
      [("SplPriorityQueue is a max-heap, so distances are negated", ["max-heap", "max heap", "negat"], 2),
       ("edge weights must be non-negative", ["non-negative", "negative weight", "negative edge"], 1),
       ("O((V+E) log V); stale queue entries get re-processed", ["log v", "stale", "lazy", "duplicate"], 1)],
      [],
      "SplPriorityQueue is a max-heap, so priorities are negated to extract the smallest distance first. Weights must "
      "be non-negative. Complexity O((V+E) log V). Stale entries (older, larger distances) are not skipped on extract, "
      "so nodes may be re-processed — check the popped distance (lazy deletion) to avoid that."),
    Q(D, "advanced", "general", "When greedy change fails",
      """Coins: 1, 3, 4
Amount: 6""",
      "Compare greedy with the optimum, then describe a DP that always finds the fewest coins and its complexity.",
      [("greedy uses 3 coins, optimum is 2 (3 + 3)", ["3 + 3", "3+3", "2 coins", "two coins"], 2),
       ("dp[a] = 1 + min over coins of dp[a − c]", ["dp[", "1 + min", "min(dp"], 1),
       ("O(amount × number of coins)", ["amount"], 0.5)],
      [],
      "Greedy takes 4 + 1 + 1 = 3 coins, but 3 + 3 uses 2 coins. DP: dp[0] = 0 and dp[a] = 1 + min(dp[a − c]) over "
      "coins c ≤ a, filled from 1 to the amount — O(amount × number of coins) time."),
]
