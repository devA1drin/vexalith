"""Seed questions: PHP (output tracing, type juggling, arrays, debugging, security review, complexity)."""

from app.content.qdef import Q

P = "php"

QUESTIONS_PHP = [
    # ── Beginner ────────────────────────────────────────────────────────────
    Q("code_tracing", "beginner", P, "Dot versus plus",
      """<?php
$a = "5";
$b = 3;
echo $a . $b, " ", $a + $b;""",
      "What is printed? Explain each operator.",
      [("prints 53 8", ["53 8", "53, 8", "53 and 8"], 2),
       (". concatenates strings, + converts to numbers", ["concaten", "numeric", "number"], 1)],
      [],
      "It prints “53 8”. The . operator concatenates (\"5\" . 3 → \"53\"); + is arithmetic, so the numeric string "
      "\"5\" is converted to a number and 5 + 3 = 8."),
    Q("debugging", "beginner", P, "strpos at position zero",
      """<?php
$email = "admin@site.com";
if (strpos($email, "admin")) {
    echo "Is admin";
}""",
      "Nothing is printed. Why, and what is the fix?",
      [("strpos returns 0, which is falsy", ["0", "falsy", "false"], 2),
       ("fix: compare !== false or use str_starts_with / str_contains", ["!== false", "str_contains", "str_starts_with"], 1)],
      [],
      "strpos returns the position 0 because “admin” is at the start, and 0 is falsy in the if. Use "
      "strpos(...) !== false, or better str_starts_with($email, \"admin\") / str_contains (PHP 8)."),
    Q("algorithmic_thinking", "beginner", P, "Duplicate check cost",
      """<?php
function hasDuplicate(array $xs): bool {
    for ($i = 0; $i < count($xs); $i++)
        for ($j = $i + 1; $j < count($xs); $j++)
            if ($xs[$i] === $xs[$j]) return true;
    return false;
}""",
      "What is the time complexity, and how would you make it faster?",
      [("O(n^2)", ["o(n^2)", "o(n²)", "quadratic", "n^2", "n squared"], 2),
       ("use a hash lookup (isset on array keys) for O(n)", ["o(n)", "isset", "hash", "array_flip", "array_unique"], 1)],
      [],
      "It is O(n^2) — every pair is compared. Track seen values as array keys and check isset($seen[$x]) for O(n) "
      "expected time (or compare count(array_unique($xs)) with count($xs))."),
    Q("edge_cases_testing", "beginner", P, "Average of nothing",
      """<?php
function average(array $xs): float {
    return array_sum($xs) / count($xs);
}""",
      "Which input breaks this function, and what should it do instead?",
      [("an empty array divides by zero", ["empty", "division by zero", "divisionbyzero", "zero"], 2),
       ("guard it: return null / throw / check count", ["guard", "null", "throw", "check"], 1)],
      [],
      "An empty array makes count() 0, so PHP 8 throws DivisionByZeroError. Guard it: check for empty input and "
      "return null or throw a meaningful exception (and decide how to treat non-numeric values)."),
    Q("code_review_design", "beginner", P, "Echoing a query parameter",
      """<p>Hello, <?php echo $_GET['name']; ?></p>""",
      "Review this line. What are the problems and the fix?",
      [("reflected XSS", ["xss", "cross-site", "inject"], 2),
       ("escape with htmlspecialchars", ["htmlspecialchars", "escape"], 1),
       ("a missing key raises a warning: use ?? or isset", ["??", "isset", "undefined"], 1)],
      [],
      "User input is echoed raw, so ?name=<script>… is reflected XSS. Escape it with htmlspecialchars($name, "
      "ENT_QUOTES, 'UTF-8'). Also a missing key raises an undefined index warning — use $_GET['name'] ?? 'guest'."),
    Q("data_structures", "beginner", P, "Duplicate array keys",
      """<?php
$m = ["a" => 1, "b" => 2, "a" => 3];
echo count($m), " ", $m["a"];""",
      "What is printed? Explain what happens to the repeated key.",
      [("prints 2 3", ["2 3", "2, 3"], 2), ("a repeated key overwrites the earlier value", ["overwrit", "replace", "duplicate"], 1)],
      [],
      "It prints “2 3”. Array keys are unique: the second \"a\" => 3 overwrites the first value (keeping its "
      "original position), so there are 2 elements and $m[\"a\"] is 3."),

    # ── Intermediate ────────────────────────────────────────────────────────
    Q("code_tracing", "intermediate", P, "Reference left behind by foreach",
      """<?php
$xs = [1, 2, 3];
foreach ($xs as &$x) { $x *= 2; }
foreach ($xs as $x) { }
print_r($xs);""",
      "What does print_r show? Explain the surprising part.",
      [("[2, 4, 4]", ["2, 4, 4", "2 4 4", "2,4,4"], 2),
       ("$x is still a reference to the last element", ["reference", "last element", "still points", "unset"], 1)],
      [],
      "It shows [2, 4, 4]. After the first loop $x is still a reference to the last element. The second loop "
      "assigns each value to $x, i.e. into $xs[2]: 2, then 4, then 4. unset($x) after a by-reference loop."),
    Q("debugging", "intermediate", P, "Loose comparison of hashes",
      """<?php
$token = $_GET['token'] ?? '';
$expected = "0e462097431906509019562988736854";
if ($token == $expected) { echo "ok"; }""",
      "An attacker sends token=0e1 and gets “ok”. Explain and fix.",
      [("both are numeric strings in scientific notation equal to 0", ["0e", "scientific", "numeric string", "equal to 0", "both are 0"], 2),
       ("use === or hash_equals", ["===", "hash_equals"], 1),
       ("hash_equals is timing-safe", ["timing"], 0.5)],
      [],
      "With ==, two numeric strings are compared as numbers: \"0e1\" and \"0e4620…\" are both scientific notation "
      "for 0, so they are equal. Use strict === or, for secrets, hash_equals($expected, $token), which is also "
      "timing-safe."),
    Q("algorithmic_thinking", "intermediate", P, "array_shift as a queue",
      """<?php
while (count($queue) > 0) {
    $job = array_shift($queue);
    process($job);
}""",
      "With 100,000 jobs this is very slow. What is the complexity and the fix?",
      [("O(n^2) overall", ["o(n^2)", "o(n²)", "quadratic"], 2),
       ("array_shift re-indexes the array (O(n) each)", ["reindex", "re-index", "renumber"], 1),
       ("use SplQueue, an index pointer or array_pop on a reversed array", ["splqueue", "pointer", "array_pop", "index"], 1)],
      [],
      "array_shift is O(n) because it re-indexes the remaining numeric keys, so the loop is O(n^2). Use SplQueue "
      "(O(1) dequeue), iterate with an index pointer, or reverse once and array_pop."),
    Q("edge_cases_testing", "intermediate", P, "Pagination parameters",
      """<?php
$page = (int)($_GET['page'] ?? 1);
$per  = (int)($_GET['per'] ?? 20);
$offset = ($page - 1) * $per;
$sql = "SELECT * FROM posts LIMIT $per OFFSET $offset";""",
      "List the edge-case inputs you would test and what each one breaks.",
      [("page 0 or negative gives a negative offset", ["negative", "page=0", "page 0"], 2),
       ("a huge per value (resource exhaustion)", ["huge", "large", "1000000", "max"], 1),
       ("clamp / validate both values", ["clamp", "max(", "min(", "validate"], 1)],
      [],
      "page=0 or negative gives a negative OFFSET (SQL error); per=0 returns nothing; per=1000000 dumps the table "
      "(resource exhaustion); “abc” casts to 0. Clamp: $page = max(1, $page); $per = min(max(1, $per), 100)."),
    Q("code_review_design", "intermediate", P, "Query built from input",
      """<?php
$id  = $_GET['id'];
$row = $pdo->query("SELECT * FROM users WHERE id = $id")->fetch();""",
      "Review this data access code.",
      [("SQL injection", ["sql injection", "injection", "inject"], 2),
       ("use prepared statements with bound parameters", ["prepare", "bind", "placeholder"], 1),
       ("validate the type (int)", ["int", "validate", "filter_var"], 0.5)],
      [],
      "Interpolating $_GET['id'] into SQL allows SQL injection (e.g. id=1 OR 1=1). Use a prepared statement: "
      "$stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?'); $stmt->execute([$id]); and validate it as an int."),
    Q("data_structures", "intermediate", P, "array_merge versus +",
      """<?php
$a = [0 => "x", 1 => "y"];
$b = [0 => "z", 5 => "w"];
print_r(array_merge($a, $b));
print_r($a + $b);""",
      "What do the two print_r calls show? Explain the difference.",
      [("array_merge renumbers: x, y, z, w", ["x, y, z, w", "x y z w", "renumber", "reindex"], 2),
       ("+ keeps the left keys and adds only missing keys (5 => w)", ["5 => w", "5=>w", "keeps", "left"], 1)],
      [],
      "array_merge renumbers numeric keys: [0 => x, 1 => y, 2 => z, 3 => w]. The + union keeps the left array's "
      "keys and only adds missing ones: [0 => x, 1 => y, 5 => w] (z is dropped because key 0 exists)."),

    # ── Advanced ────────────────────────────────────────────────────────────
    Q("code_tracing", "advanced", P, "Static counter and closure by reference",
      """<?php
function counter() {
    static $n = 0;
    return ++$n;
}
$f = function () use (&$total) { $total += counter(); };
$total = 0;
$f(); $f(); $f();
echo $total;""",
      "What is echoed? Explain both the static variable and the use clause.",
      [("6", ["6"], 2), ("static keeps its value between calls (1, 2, 3)", ["static", "persist"], 1),
       ("use (&$total) binds by reference, so later assignment is seen", ["reference", "&$total"], 1)],
      [],
      "It echoes 6. static $n persists between calls, so counter() returns 1, 2, 3. use (&$total) captures by "
      "reference, so the closure sees $total = 0 set after it was created: 0 + 1 + 2 + 3 = 6."),
    Q("debugging", "advanced", P, "Comparing money floats",
      """<?php
$total = 0.1 + 0.2;
if ($total == 0.3) { echo "equal"; } else { echo "not equal"; }""",
      "What is printed, why, and how should money be handled?",
      [("prints not equal", ["not equal"], 2),
       ("binary floating point cannot represent 0.1 exactly", ["binary", "floating", "precision"], 1),
       ("use integer cents / bcmath / an epsilon", ["cents", "bcmath", "epsilon", "round"], 1)],
      [],
      "It prints “not equal”: 0.1 and 0.2 have no exact binary floating-point representation, so the sum is "
      "0.30000000000000004. Store money as integer cents (or use bcmath/brick/money); compare floats with an epsilon."),
    Q("algorithmic_thinking", "advanced", P, "Memoized Fibonacci",
      """<?php
function fib(int $n, array &$memo = []): int {
    if ($n < 2) return $n;
    if (isset($memo[$n])) return $memo[$n];
    return $memo[$n] = fib($n - 1, $memo) + fib($n - 2, $memo);
}""",
      "Give the time and space complexity with and without the memo, and one limitation.",
      [("O(n) time with the memo", ["o(n)"], 2),
       ("exponential O(2^n) without it", ["exponential", "2^n", "o(2^n)"], 1),
       ("recursion depth / stack; an iterative version uses O(1) space", ["stack", "depth", "iterative"], 1)],
      [],
      "With the memo each n is computed once: O(n) time and O(n) space (memo plus call stack). Without it the "
      "recursion is exponential, about O(2^n). Recursion depth grows with n; an iterative loop needs O(1) space."),
    Q("edge_cases_testing", "advanced", P, "Truncating UTF-8",
      """<?php
function truncate(string $s, int $max): string {
    return strlen($s) > $max ? substr($s, 0, $max) . "…" : $s;
}
echo truncate("Café ☕ time", 4);""",
      "What goes wrong for non-ASCII text, and how do you fix it?",
      [("strlen/substr work on bytes and can cut a multibyte character", ["byte", "multibyte", "utf-8", "utf8"], 2),
       ("use mb_strlen / mb_substr", ["mb_substr", "mb_strlen", "mb_"], 1),
       ("graphemes and the ellipsis length", ["grapheme", "ellipsis"], 0.5)],
      [],
      "strlen and substr count bytes, not characters. “é” is 2 bytes in UTF-8, so substr($s, 0, 4) keeps “Caf” "
      "plus only the first byte of “é” — invalid UTF-8 that renders as �. Use mb_strlen/mb_substr (or "
      "grapheme_substr for emoji clusters), and account for the ellipsis in the length."),
    Q("code_review_design", "advanced", P, "Storing passwords",
      """<?php
$hash = md5($_POST['password']);
$stmt = $pdo->prepare("INSERT INTO users (email, pass) VALUES (?, ?)");
$stmt->execute([$_POST['email'], $hash]);""",
      "Review how the password is stored.",
      [("md5 is fast and unsalted, so it is easy to brute-force", ["fast", "unsalted", "salt", "rainbow", "brute"], 2),
       ("use password_hash / password_verify (bcrypt or Argon2)", ["password_hash", "password_verify", "bcrypt", "argon"], 2),
       ("the prepared statement itself is fine", ["prepared"], 0.5)],
      [],
      "md5 is a fast, unsalted hash, so leaked hashes fall to rainbow tables and brute force. Use "
      "password_hash($pw, PASSWORD_DEFAULT) (bcrypt/Argon2, salted) and password_verify at login. The prepared "
      "statement is fine."),
    Q("data_structures", "advanced", P, "Top 10 from a stream",
      """<?php
// keep the 10 highest scores from a stream of millions
$top = [];
foreach ($stream as $score) {
    $top[] = $score;
    rsort($top);
    $top = array_slice($top, 0, 10);
}""",
      "Which data structure fits better, and what is the resulting complexity?",
      [("a min-heap of size k (SplMinHeap)", ["min-heap", "min heap", "splminheap", "heap"], 2),
       ("O(n log k)", ["n log k", "o(n log k)"], 1),
       ("compare each score to the heap's minimum before inserting", ["minimum", "smallest", "top", "min"], 1)],
      [],
      "Use a min-heap of size k (SplMinHeap): compare each score with the heap's minimum (top) and only replace it "
      "when larger. That is O(n log k) time and O(k) memory, without re-sorting and slicing arrays on every item."),
]
