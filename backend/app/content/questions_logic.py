"""Seed questions: Logic Problems (language-agnostic; tagged language="general")."""

from app.content.qdef import Q

G = "general"
D = "logic_problems"

QUESTIONS_LOGIC = [
    # ── Beginner ────────────────────────────────────────────────────────────
    Q(D, "beginner", G, "When is an implication true?",
      """P → Q   (if P then Q)

row 1:  P = false,  Q = true
row 2:  P = false,  Q = false
row 3:  P = true,   Q = false""",
      "For which rows is P → Q true? Justify using the truth table of implication.",
      [("rows 1 and 2 are true, row 3 is false", ["rows 1 and 2", "row 3 is false", "only when p is true", "only false when"], 2),
       ("a false premise makes it vacuously true", ["vacuous", "false premise"], 1)],
      [("thinks a false premise makes it false", ["row 1 is false", "row 2 is false"], "With a false premise the implication is vacuously true.")],
      "Rows 1 and 2 are true and row 3 is false. P → Q is only false when P is true and Q is false; when the premise "
      "P is false the implication is vacuously true."),
    Q(D, "beginner", G, "De Morgan's law",
      """not (A and B)

(a)  not A and not B
(b)  not A or not B
(c)  A or B""",
      "Which option is equivalent? Explain the rule.",
      [("(b) not A or not B", ["(b)", "option b", "not a or not b"], 2), ("De Morgan: negation flips and/or", ["de morgan", "flip"], 1)],
      [("picks (a)", ["(a) is", "answer is a", "option a"], "not A and not B is the negation of (A or B), not of (A and B).")],
      "(b) not A or not B. By De Morgan's law, negating a conjunction flips it into a disjunction of the negations: "
      "not (A and B) ≡ not A or not B."),
    Q(D, "beginner", G, "Knights and knaves",
      """Knights always tell the truth. Knaves always lie.
A says: "We are both knaves."
What are A and B?""",
      "Determine A and B and show why the alternative is impossible.",
      [("A is a knave, B is a knight", ["a is a knave", "a is knave", "b is a knight", "b is knight"], 2),
       ("A cannot be a knight (contradiction)", ["contradict", "cannot be a knight", "can't be a knight", "would be lying"], 1)],
      [],
      "A is a knave and B is a knight. If A were a knight, the statement “we are both knaves” would make A a knave — "
      "a contradiction. So A is a knave and the statement is false, meaning not both are knaves: B is a knight."),
    Q(D, "beginner", G, "Short-circuit guard",
      """x = 0
if x != 0 and 10 / x > 1:
    print("big")
else:
    print("small")""",
      "What happens? Is there a division-by-zero error?",
      [("prints small", ["small"], 2),
       ("short-circuit: the division is never evaluated", ["short-circuit", "short circuit", "never evaluated", "not evaluated", "skips"], 1)],
      [("expects a crash", ["zerodivisionerror", "crash", "error is raised"], "The `and` short-circuits: once x != 0 is false, 10 / x is never evaluated.")],
      "It prints “small” with no error. `and` short-circuits: x != 0 is false, so 10 / x is never evaluated and "
      "the else branch runs."),
    Q(D, "beginner", G, "Next in the sequence",
      """2, 6, 12, 20, 30, ?""",
      "What comes next? Describe the rule you found.",
      [("42", ["42"], 2), ("differences grow by 2 / n(n+1)", ["n(n+1)", "difference", "+12", "increase by 2"], 1)],
      [],
      "42. The differences are 4, 6, 8, 10, so the next difference is 12 (30 + 12). Equivalently the nth term is "
      "n(n+1): 1·2, 2·3, …, 6·7 = 42."),
    Q(D, "beginner", G, "Neither language",
      """30 students.
18 study Python, 15 study JavaScript, 7 study both.""",
      "How many study neither? Show the reasoning.",
      [("4", ["4", "four"], 2), ("inclusion–exclusion: subtract the overlap once", ["inclusion", "exclusion", "26", "overlap", "subtract"], 1)],
      [("forgets the overlap", ["-3", "negative"], "Adding 18 + 15 counts the 7 students in both twice; subtract them once.")],
      "4. By inclusion–exclusion, at least one language = 18 + 15 − 7 = 26 (the overlap is counted twice, so "
      "subtract it once). Neither = 30 − 26 = 4."),
    Q(D, "beginner", G, "Contrapositive",
      """Rule: "If the build passes, then all tests ran."

(a) If all tests ran, the build passes.
(b) If not all tests ran, the build did not pass.
(c) If the build fails, some tests did not run.""",
      "Which statement must be true? Name the other two.",
      [("(b) is the contrapositive", ["(b)", "option b"], 2), ("contrapositive is equivalent", ["contrapositive"], 1),
       ("(a) is the converse, (c) the inverse", ["converse", "inverse"], 1)],
      [],
      "(b) must be true — it is the contrapositive (not Q → not P), which is logically equivalent. (a) is the converse "
      "and (c) is the inverse; neither follows from the rule."),
    Q(D, "beginner", G, "Simplify a boolean expression",
      """(A and B) or (A and not B)""",
      "Simplify the expression and justify each step.",
      [("it simplifies to A", ["simplifies to a", "= a", "equals a", "just a", "reduces to a"], 2),
       ("factor A out; B or not B is always true", ["factor", "distribut", "b or not b", "always true"], 1)],
      [],
      "It simplifies to A. Factor A out with the distributive law: A and (B or not B). B or not B is always true, so "
      "the result is A and true = A."),

    # ── Intermediate ────────────────────────────────────────────────────────
    Q(D, "intermediate", G, "Parity of three inputs",
      """(A xor B) xor C""",
      "In the 8-row truth table, how many rows are true, and which ones?",
      [("4 rows", ["4", "four"], 2), ("true when an odd number of inputs are true (parity)", ["odd", "parity"], 1)],
      [],
      "4 of the 8 rows are true: exactly those with an odd number of true inputs (one or three), because chained XOR "
      "computes parity."),
    Q(D, "intermediate", G, "Loop invariant for a sum",
      """i = 0
s = 0
while i < n:
    s = s + a[i]
    i = i + 1
# claim: s == a[0] + ... + a[n-1]""",
      "State a loop invariant and use it to prove the claim.",
      [("invariant: s equals the sum of the first i elements", ["first i", "a[0..i-1]", "a[0:i]", "sum of a[0"], 2),
       ("initialization, maintenance and termination", ["initial", "maintain", "terminat"], 1),
       ("at exit i == n", ["i == n", "i = n", "i=n"], 1)],
      [],
      "Invariant: s equals the sum of the first i elements, a[0..i-1], and 0 ≤ i ≤ n. Initialization: i = 0, s = 0 "
      "(empty sum). Maintenance: adding a[i] then incrementing i preserves it. Termination: the loop stops when "
      "i == n, so s is the sum of all n elements."),
    Q(D, "intermediate", G, "Who broke the build?",
      """Ana: "Ben broke the build."
Ben: "Cy broke the build."
Cy:  "I didn't break it."
Exactly one of them is lying, and exactly one person broke it.""",
      "Who broke the build? Show the case analysis.",
      [("Ben broke it", ["ben broke", "it was ben", "ben is guilty", "ben did it", "culprit is ben"], 2),
       ("check each case", ["case", "assume", "suppose", "if ana", "if cy"], 1)],
      [],
      "Ben broke it. Case Ana guilty: Ana and Ben lie (two liars) ✗. Case Cy guilty: Ana and Cy lie ✗. Case Ben "
      "guilty: only Ben lies ✓ — Ana's and Cy's statements are true. So the culprit is Ben."),
    Q(D, "intermediate", G, "Negating 'every'",
      """"Every request has a valid token.\"""",
      "Write the logical negation of this statement in plain English.",
      [("some request does not have a valid token", ["some request", "at least one", "there exists", "there is a request"], 2),
       ("not-all becomes there-exists-not", ["exists", "quantifier", "∃"], 1)],
      [("negates to 'no request has a valid token'", ["no request has"], "That is too strong; the negation of “all” is “not all”, i.e. at least one does not.")],
      "“At least one request does not have a valid token.” Negating a universal statement gives an existential: "
      "not (for all x, P(x)) ≡ there exists x with not P(x)."),
    Q(D, "intermediate", G, "Doubling sequence",
      """1, 3, 7, 15, 31, ?""",
      "What comes next? Give a closed form.",
      [("63", ["63"], 2), ("2^n − 1 (double and add one)", ["2^n", "double", "2n+1", "times 2", "×2", "*2"], 1)],
      [],
      "63. Each term is double the previous plus one (31·2 + 1), i.e. the nth term is 2^n − 1."),
    Q(D, "intermediate", G, "Pigeonhole buckets",
      """A hash function maps usernames into 100 buckets.""",
      "How many usernames guarantee that at least two share a bucket? Why?",
      [("101", ["101"], 2), ("pigeonhole principle", ["pigeonhole"], 1)],
      [],
      "101. With 100 buckets, 100 names could all land in different buckets, but by the pigeonhole principle the 101st "
      "must share a bucket with an earlier one."),
    Q(D, "intermediate", G, "Satisfying assignments",
      """(a or b) and not c""",
      "List every assignment of (a, b, c) that makes the expression true.",
      [("exactly 3 assignments", ["3", "three"], 2), ("c must be false", ["c must be false", "c is false", "c = false", "not c"], 1),
       ("at least one of a, b true", ["at least one"], 1)],
      [],
      "Three assignments: (T, T, F), (T, F, F), (F, T, F). c must be false (not c), and at least one of a or b must "
      "be true."),
    Q(D, "intermediate", G, "Set operations",
      """A = {1, 2, 3, 4}
B = {3, 4, 5}""",
      "Compute the symmetric difference A △ B, the difference A − B and the intersection A ∩ B.",
      [("A △ B = {1, 2, 5}", ["{1, 2, 5}", "{1,2,5}"], 2), ("A − B = {1, 2}", ["{1, 2}", "{1,2}"], 1),
       ("A ∩ B = {3, 4}", ["{3, 4}", "{3,4}"], 1)],
      [],
      "A △ B = {1, 2, 5} (in exactly one set), A − B = {1, 2} (in A but not B) and A ∩ B = {3, 4} (in both)."),

    # ── Advanced ────────────────────────────────────────────────────────────
    Q(D, "advanced", G, "Mislabeled boxes",
      """Three boxes are labeled "Apples", "Oranges" and "Mixed".
Every label is wrong.
You may take one fruit from one box (without looking inside).""",
      "Which box do you pick from, and how do you relabel all three?",
      [("pick from the box labeled Mixed", ["mixed"], 2),
       ("that box must be pure because every label is wrong", ["every label is wrong", "labels are wrong", "must be pure", "cannot be mixed", "can't be mixed"], 1),
       ("the other two follow by elimination", ["eliminat", "remaining", "the other two"], 1)],
      [],
      "Take a fruit from the box labeled “Mixed”. Since every label is wrong, it must be pure — if you draw an apple "
      "it is the Apples box. The box labeled “Oranges” can't be oranges and isn't apples, so it is Mixed; the "
      "remaining box is Oranges (by elimination; symmetric if you draw an orange)."),
    Q(D, "advanced", G, "Breaking a chocolate bar",
      """A 6 × 4 chocolate bar (24 squares).
Each break splits one piece into two along a line.""",
      "What is the minimum number of breaks to get 24 single squares? Prove it.",
      [("23", ["23"], 2), ("each break increases the number of pieces by exactly one", ["exactly one", "by one", "by 1", "one piece", "increases the number"], 1)],
      [],
      "23, regardless of strategy. Invariant: every break increases the number of pieces by exactly one, starting "
      "from 1 piece. Reaching 24 pieces therefore needs exactly 23 breaks."),
    Q(D, "advanced", G, "Resolution simplification",
      """(A or B) and (A or not B) and (not A or C)""",
      "Simplify to the smallest equivalent expression and justify each step.",
      [("A and C", ["a and c", "a ∧ c", "a && c"], 2),
       ("(A or B) and (A or not B) reduces to A", ["reduces to a", "simplifies to a", "= a", "distribut", "resolution"], 1)],
      [],
      "A and C. First, (A or B) and (A or not B) = A or (B and not B) = A (distributive law). Then A and (not A or C) "
      "= (A and not A) or (A and C) = A and C."),
    Q(D, "advanced", G, "Hundred lockers",
      """100 closed lockers. Student k (k = 1..100) toggles
every k-th locker (k, 2k, 3k, ...).""",
      "How many lockers are open at the end, and which ones? Why?",
      [("10 lockers", ["10", "ten"], 2), ("the perfect squares", ["perfect square", "square number", "squares"], 1),
       ("only squares have an odd number of divisors", ["odd number of divisors", "divisors"], 1)],
      [],
      "10 lockers: 1, 4, 9, …, 100 — the perfect squares. Locker n is toggled once per divisor of n; divisors come in "
      "pairs except for square numbers, so only squares have an odd number of divisors and end open."),
    Q(D, "advanced", G, "Induction step",
      """Claim: 1 + 3 + 5 + ... + (2n − 1) = n²  for all n ≥ 1""",
      "Prove the claim by induction. Make the inductive step explicit.",
      [("adding 2n + 1 to n² gives (n + 1)²", ["2n+1", "2n + 1", "(n+1)²", "(n+1)^2", "(n + 1)^2"], 2),
       ("base case n = 1", ["base case", "n = 1", "n=1"], 1), ("inductive hypothesis", ["hypothesis", "assume"], 1)],
      [],
      "Base case n = 1: 1 = 1². Inductive hypothesis: assume the sum of the first n odd numbers is n². The next odd "
      "number is 2(n+1) − 1 = 2n + 1, and n² + 2n + 1 = (n + 1)², so the claim holds for n + 1."),
    Q(D, "advanced", G, "Deployment schedule",
      """Services A, B and C deploy on Mon, Tue and Wed (one per day).
- B does not deploy on Monday.
- C deploys the day after A.""",
      "Which day does each service deploy? Show the case analysis.",
      [("A on Monday, C on Tuesday, B on Wednesday", ["b on wednesday", "b wednesday", "b deploys on wednesday"], 2),
       ("case split on A's day / elimination", ["case", "if a", "eliminat", "only two"], 1)],
      [],
      "A on Monday, C on Tuesday, B on Wednesday. C after A allows only two cases: (A Mon, C Tue) leaves B on Wed, "
      "which is allowed; (A Tue, C Wed) forces B onto Monday, which is forbidden — eliminated."),
    Q(D, "advanced", G, "Precedence and side effects",
      """calls = 0
def check(v):
    global calls
    calls += 1
    return v

r = check(False) and check(True) or check(True)""",
      "What are r and calls afterwards? Explain the evaluation order.",
      [("r is True and check runs 2 times", ["2 calls", "two calls", "calls = 2", "calls == 2", "called twice", "2 times"], 2),
       ("and binds tighter than or", ["precedence", "binds tighter", "higher precedence"], 1),
       ("the middle check is skipped by short-circuit", ["short-circuit", "short circuit", "skipped", "not evaluated"], 1)],
      [],
      "r is True and calls = 2. `and` has higher precedence: (check(False) and check(True)) or check(True). "
      "check(False) is false, so check(True) inside the and is skipped by short-circuit; then `or` evaluates the "
      "last check(True)."),
    Q(D, "advanced", G, "Why the subtraction loop stops",
      """# a, b are positive integers
while a != b:
    if a > b:
        a = a - b
    else:
        b = b - a""",
      "Argue that the loop terminates and say what it computes.",
      [("it computes the gcd", ["gcd", "greatest common divisor"], 2),
       ("a + b strictly decreases while both stay positive (a variant)", ["decreas", "variant"], 1),
       ("gcd(a, b) is preserved (invariant)", ["invariant", "preserv"], 1)],
      [],
      "It computes gcd(a, b). Termination: each step keeps a and b positive and strictly decreases a + b (a variant), "
      "so it cannot go on forever. Correctness: gcd(a, b) = gcd(a − b, b) is preserved as an invariant, and when "
      "a == b, the gcd is a."),
]
