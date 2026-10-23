"""Seed questions for Java across core reasoning domains and algorithms (21 questions)."""

from app.content.qdef import Q

J = "java"

QUESTIONS_JAVA = [
    # ── Beginner (7) ────────────────────────────────────────────────────────
    Q("code_tracing", "beginner", J, "Post-increment vs pre-increment in Java",
      """int a = 5;
int b = a++;
int c = ++a;
System.out.println(a + " " + b + " " + c);""",
      "What does this print? Trace the value of a, b, and c after each line.",
      [("prints 7 5 7", ["7 5 7"], 2),
       ("a++ returns the old value (5) for b and then increments a to 6; ++a increments a to 7 first and returns 7 for c", ["old value", "before", "after", "6", "a++", "++a"], 1.5)],
      [("thinks it prints 7 6 7", ["7 6 7"], "Post-increment a++ yields 5 before incrementing a to 6, so b is 5.")],
      "It prints 7 5 7. On `int b = a++`, post-increment yields `a`'s current value (`5`) for `b` and then increments "
      "`a` to `6`. On `int c = ++a`, pre-increment increments `a` to `7` first and assigns `7` to `c`."),

    Q("debugging", "beginner", J, "Comparing Strings with == in a role check",
      """static boolean isAdmin(String role) {
    return role == "admin";
}""",
      "Why can isAdmin(role) return false even when role contains \"admin\", and what is the null-safe fix?",
      [("== checks reference identity (same object in memory), not whether the String characters match", ["reference", "same object", "identity", "memory"], 2),
       ("fix: write \"admin\".equals(role), which compares characters and safely returns false if role is null", ["\"admin\".equals(role)", "equals("], 1.5)],
      [],
      "`role == \"admin\"` compares object references rather than String contents, so any String constructed at "
      "runtime (from user input, JSON, or `new String(\"admin\")`) can return false. Fix it with "
      "`\"admin\".equals(role)`, which compares character content and safely returns false when `role` is `null`."),

    Q("algorithmic_thinking", "beginner", J, "Repeated String concatenation in a loop",
      """String csv = "";
for (int i = 0; i < n; i++) {
    csv += i + ",";
}""",
      "What is the time complexity of this loop in Java as n grows, why, and how do you make it O(n)?",
      [("O(n^2) time because Java Strings are immutable and each += allocates a new String and copies all previous characters", ["o(n^2)", "quadratic", "immutab", "copies", "new string"], 2),
       ("use StringBuilder and append(...) inside the loop for O(n) total time", ["stringbuilder", "append", "o(n)"], 1.5)],
      [("thinks it is O(n) because the loop runs n times", ["is o(n) because"], "The loop runs n times, but step k copies O(k) characters into a new String, summing to O(n^2).") ],
      "It runs in O(n^2) time. Because Java Strings are immutable, each `csv += ...` allocates a brand-new String "
      "and copies every character accumulated so far (1 + 2 + ... + n = O(n^2) copies). Use a `StringBuilder` with "
      "`sb.append(i).append(\",\")` and `sb.toString()` at the end for O(n) time."),

    Q("edge_cases_testing", "beginner", J, "Average of an int[] array in Java",
      """static double average(int[] nums) {
    int sum = 0;
    for (int x : nums) {
        sum += x;
    }
    return sum / nums.length;
}""",
      "Identify at least three bugs or edge-case failures in average(int[] nums).",
      [("empty array (nums.length == 0) throws ArithmeticException: / by zero, and null nums throws NullPointerException", ["empty", "length == 0", "arithmeticexception", "by zero", "null"], 2),
       ("sum / nums.length performs integer division and truncates the fractional part before converting to double (use (double) sum / nums.length)", ["integer division", "truncat", "(double)"], 1.5),
       ("int sum can overflow for large arrays or large ints (use long sum)", ["overflow", "long"], 1)],
      [],
      "Three issues: (1) if `nums` is empty (`nums.length == 0`) it throws `ArithmeticException: / by zero` (and "
      "`NullPointerException` if `nums == null`); (2) `sum / nums.length` divides two `int`s and truncates the "
      "decimal before widening to `double`—cast `(double) sum / nums.length`; (3) `int sum` can overflow 32-bit "
      "range, so accumulate into a `long`."),

    Q("code_review_design", "beginner", J, "Swallowing exceptions with an empty catch block",
      """try {
    saveOrder(order);
} catch (Exception e) {
}""",
      "Why is an empty catch (Exception e) {} dangerous in production code, and what should be done instead?",
      [("silently hides failures so the caller thinks saveOrder succeeded while data is lost or corrupt", ["silent", "hides", "swallow", "data loss", "caller"], 2),
       ("catch specific exception types, log/propagate or wrap and rethrow, and do not catch broad Exception/RuntimeException silently", ["specific", "rethrow", "log", "propagate"], 1.5)],
      [],
      "An empty `catch (Exception e) {}` swallows every failure (including `NullPointerException` and database errors), "
      "leaving callers to proceed as if the order was saved while hiding the stack trace. Catch only specific "
      "recoverable exceptions, or log the context and rethrow/propagate the failure."),

    Q("data_structures", "beginner", J, "Finding duplicates: nested loops vs HashSet",
      """static boolean hasDuplicate(int[] nums) {
    for (int i = 0; i < nums.length; i++) {
        for (int j = i + 1; j < nums.length; j++) {
            if (nums[i] == nums[j]) return true;
        }
    }
    return false;
}""",
      "What is the time complexity of hasDuplicate, and which Java collection lowers it to O(n) average time?",
      [("O(n^2) time now; using HashSet<Integer> (seen.add(x)) gives O(n) average time and O(n) space", ["o(n^2)", "hashset", "o(n)"], 2),
       ("HashSet.add(x) returns false in O(1) average time as soon as x is already present", ["add(", "contains", "o(1)", "already"], 1.5)],
      [],
      "The nested loops compare all pairs in O(n^2) time and O(1) space. Using a `Set<Integer> seen = new HashSet<>()` "
      "and checking `if (!seen.add(x)) return true;` checks and inserts each number in O(1) average time, reducing "
      "total time to O(n) with O(n) space."),

    Q("algorithms", "beginner", J, "Binary search on a sorted Java array",
      """static int binarySearch(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}""",
      "Why does this run in O(log n) time, and why is lo + (hi - lo) / 2 preferred over (lo + hi) / 2 in Java?",
      [("each comparison halves the remaining search interval [lo, hi], giving O(log n) time and O(1) space", ["halves", "half", "o(log n)", "o(1)"], 2),
       ("(lo + hi) can overflow 32-bit signed int into a negative number when lo + hi > Integer.MAX_VALUE, whereas lo + (hi - lo) / 2 never overflows", ["overflow", "max_value", "negative", "hi - lo"], 1.5)],
      [],
      "Because `a` is sorted, each comparison eliminates half of the remaining range `[lo, hi]`, taking O(log n) "
      "time and O(1) space. Writing `lo + (hi - lo) / 2` (or `(lo + hi) >>> 1`) avoids 32-bit signed `int` overflow "
      "when `lo + hi` exceeds `Integer.MAX_VALUE`, which would make `(lo + hi) / 2` negative."),

    # ── Intermediate (7) ────────────────────────────────────────────────────
    Q("code_tracing", "intermediate", J, "Pass-by-value of object references in Java",
      """static class Box {
    int v;
    Box(int v) { this.v = v; }
}
static void update(Box b) {
    b.v = 20;
    b = new Box(99);
    b.v = 77;
}
public static void main(String[] args) {
    Box x = new Box(10);
    update(x);
    System.out.println(x.v);
}""",
      "What does main print, and why doesn't b = new Box(99) affect x in main?",
      [("prints 20", ["20", "prints 20"], 2),
       ("b starts as a copy of the reference to x's Box so b.v = 20 mutates x.v, then b = new Box(99) only rebinds the local parameter b to a new Box without changing x", ["copy of the reference", "local parameter", "rebind", "reassign", "b.v = 20"], 1.5)],
      [("thinks it prints 77 or 99", ["prints 77", "prints 99"], "Java passes object references by value; reassigning parameter b inside update does not change what x points to in main.")],
      "It prints 20. `update` receives a copy of the reference pointing to the `Box(10)` created in `main`, so "
      "`b.v = 20` mutates that object's `v` field to 20. Then `b = new Box(99)` only points the local variable `b` "
      "at a new `Box`; `x` in `main` still points to the first `Box` whose `v` is 20."),

    Q("debugging", "intermediate", J, "Removing matching items while indexing forward",
      """static void dropZeros(List<Integer> nums) {
    for (int i = 0; i < nums.size(); i++) {
        if (nums.get(i) == 0) {
            nums.remove(i);
        }
    }
}""",
      "Give an input list where dropZeros leaves a 0 behind, explain why, and show how to fix it.",
      [("fails on consecutive zeros such as [0, 0, 1] (leaves [0, 1])", ["[0, 0", "consecutive", "back-to-back", "adjacent"], 2),
       ("nums.remove(i) shifts all later elements left into index i, and then i++ skips the element that just shifted into index i", ["shift", "skips", "i++"], 1.5),
       ("fix: use nums.removeIf(x -> x == 0), iterate backwards from nums.size() - 1, or decrement i-- on removal", ["removeif", "backwards", "i--", "iterator"], 1)],
      [],
      "On `[0, 0, 1]`, removing index 0 shifts the second `0` into index 0, and then the loop's `i++` advances `i` "
      "to 1, skipping the second `0` and leaving `[0, 1]`. Fix it with `nums.removeIf(x -> x == 0);` (or iterate "
      "backwards from `nums.size() - 1` down to `0`)."),

    Q("algorithmic_thinking", "intermediate", J, "Draining a queue with ArrayList.remove(0)",
      """List<String> jobs = new ArrayList<>(initialJobs);
while (!jobs.isEmpty()) {
    String next = jobs.remove(0);
    process(next);
}""",
      "What is the total time complexity of draining n jobs with ArrayList.remove(0), and which Java class makes it O(n)?",
      [("O(n^2) total time because ArrayList.remove(0) shifts all remaining elements left by one slot on every removal", ["o(n^2)", "shift", "remove(0)"], 2),
       ("use ArrayDeque<String> with pollFirst() / removeFirst() so each removal from the front is O(1) amortized and total time is O(n)", ["arraydeque", "queue", "poll", "removefirst", "o(1)", "o(n)"], 1.5)],
      [],
      "It takes O(n^2) total time. Removing index 0 from an `ArrayList` shifts the remaining `k - 1` elements left "
      "in memory (`(n-1) + (n-2) + ... + 1 = O(n^2)`). Replace `ArrayList` with `ArrayDeque<String>` (a circular "
      "buffer) and call `jobs.pollFirst()`, which removes from the front in O(1) time for O(n) total."),

    Q("edge_cases_testing", "intermediate", J, "Parsing a TCP port from a String",
      """static int parsePort(String raw) {
    return Integer.parseInt(raw);
}""",
      "List the inputs that break or produce an invalid TCP port in parsePort, and how to harden it.",
      [("null or non-numeric strings (\"\", \"abc\", \"8080 \") throw NumberFormatException", ["null", "empty", "numberformatexception", "whitespace", "trim"], 2),
       ("valid ints outside 1..65535 (e.g. 0, -80, 70000) are returned without range validation", ["65535", "negative", "0", "range"], 1.5)],
      [],
      "`Integer.parseInt(raw)` throws `NumberFormatException` on `null`, `\"\"`, leading/trailing spaces (`\" 80 \"`), "
      "non-digits (`\"http\"`), or numbers overflowing `int`, and it accepts invalid port numbers like `-1`, `0`, "
      "or `70000`. Harden it by checking `raw != null`, calling `raw.trim()`, catching `NumberFormatException`, and "
      "verifying `1 <= port && port <= 65535`."),

    Q("code_review_design", "intermediate", J, "Returning a mutable internal List from a getter",
      """public class Course {
    private final List<String> students = new ArrayList<>();
    public void enroll(String name) { students.add(name); }
    public List<String> getStudents() { return students; }
}""",
      "How can a caller break Course's encapsulation through getStudents(), and how should getStudents() be written?",
      [("a caller can call course.getStudents().clear() or .add(...) to mutate the private list directly, bypassing enroll()", ["clear", "mutate", "directly", "bypass", "encapsulat"], 2),
       ("return Collections.unmodifiableList(students) or List.copyOf(students) so callers get a read-only view/copy", ["unmodifiablelist", "list.copyof", "defensive copy", "read-only"], 1.5)],
      [],
      "Even though `students` is `private final`, returning the `ArrayList` reference directly lets any caller write "
      "`course.getStudents().clear()` or `.add(null)` and mutate internal state behind `Course`'s back. Return "
      "`Collections.unmodifiableList(students)` or `List.copyOf(students)` instead."),

    Q("data_structures", "intermediate", J, "Counting word frequencies with HashMap",
      """Map<String, Integer> counts = new HashMap<>();
for (String w : words) {
    counts.put(w, counts.getOrDefault(w, 0) + 1);
}""",
      "Explain how counts.getOrDefault(w, 0) + 1 works on the first vs second occurrence of a word, and state the time complexity for n words.",
      [("first time w is absent so getOrDefault returns 0 and stores 1; next time it returns the existing count and increments it", ["first", "absent", "returns 0", "existing", "increment"], 2),
       ("O(n) average time and O(u) space (u unique words) because HashMap getOrDefault and put are O(1) average", ["o(n)", "o(1)", "average"], 1.5)],
      [],
      "When `w` is seen for the first time, `counts.getOrDefault(w, 0)` returns `0`, so `put(w, 1)` records 1. On "
      "later occurrences, `getOrDefault` returns the current count `c` and `put(w, c + 1)` updates it. Because "
      "`HashMap` lookup and insertion are O(1) on average, counting `n` words takes O(n) average time."),

    Q("algorithms", "intermediate", J, "Two-sum indices in one pass with HashMap",
      """static int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (seen.containsKey(need)) {
            return new int[]{seen.get(need), i};
        }
        seen.put(nums[i], i);
    }
    return new int[]{};
}""",
      "Why do we check seen.containsKey(need) before seen.put(nums[i], i), and what are the time and space complexities?",
      [("checking before inserting prevents pairing an element nums[i] with itself at the same index when target == 2 * nums[i], while still matching duplicate values at different indices", ["itself", "same index", "before", "duplicate"], 2),
       ("O(n) average time and O(n) space", ["o(n) time", "o(n) average", "o(n) space", "linear"], 1.5)],
      [],
      "Checking `seen.containsKey(need)` before `seen.put(nums[i], i)` ensures `nums[i]` is only paired with an "
      "earlier index `j < i`, never with itself when `need == nums[i]`, while still working if a second copy of the "
      "same number appears later. Each step does O(1) average `HashMap` work: O(n) time and O(n) space."),

    # ── Advanced (7) ────────────────────────────────────────────────────────
    Q("code_tracing", "advanced", J, "A return inside finally overrides try and suppresses exceptions",
      """static int compute() {
    try {
        throw new RuntimeException("boom");
    } finally {
        return 42;
    }
}
public static void main(String[] args) {
    System.out.println(compute());
}""",
      "What happens when main runs, and why is returning from a finally block considered a serious anti-pattern in Java?",
      [("prints 42 without throwing RuntimeException", ["42", "prints 42", "without throwing", "does not throw"], 2),
       ("a return in finally discards any in-flight exception (and overwrites any return value from try/catch), hiding crashes completely", ["suppress", "discard", "swallow", "overwrit", "hiding"], 1.5)],
      [("thinks RuntimeException crashes the program", ["crashes", "throws runtimeexception"], "In Java, a return statement inside finally abruptly completes the method with 42 and discards the thrown exception.")],
      "It prints 42 and never throws `RuntimeException(\"boom\")`. In Java, executing `return` inside `finally` "
      "replaces any return value or thrown exception from the `try`/`catch` block, silently discarding the "
      "`RuntimeException`."),

    Q("debugging", "advanced", J, "Mutating a HashMap key after insertion",
      """Map<List<Integer>, String> map = new HashMap<>();
List<Integer> key = new ArrayList<>(List.of(1, 2));
map.put(key, "found");
key.add(3);
System.out.println(map.get(key));""",
      "What does map.get(key) print, why can't HashMap find the entry, and what rule does this illustrate?",
      [("prints null", ["null", "prints null"], 2),
       ("key.add(3) changes key.hashCode(), so map.get(key) hashes to a different bucket than where key was stored during put", ["hashcode", "bucket", "different hash"], 1.5),
       ("always use immutable objects (e.g. List.of(1, 2), String, Integer, records) as HashMap keys or HashSet elements", ["immutab", "list.of", "record"], 1)],
      [("thinks it prints found because key is the same object", ["prints found"], "HashMap first jumps to the bucket for key.hashCode(); mutating key changed its hashCode so get looks in the wrong bucket.")],
      "It prints null. `map.put(key, \"found\")` stored the entry in the bucket corresponding to `[1, 2].hashCode()`. "
      "When `key.add(3)` mutates the list, `key.hashCode()` changes to the hash of `[1, 2, 3]`, so `map.get(key)` "
      "searches a different bucket and misses the entry. Never mutate an object while it is used as a `Map` key or "
      "`Set` element; use immutable keys such as `List.of(...)` or Java `record`s."),

    Q("algorithmic_thinking", "advanced", J, "Indexed get(i) loop over a Java LinkedList",
      """static long sum(LinkedList<Integer> list) {
    long total = 0;
    for (int i = 0; i < list.size(); i++) {
        total += list.get(i);
    }
    return total;
}""",
      "What is the time complexity of sum on a LinkedList of n elements, why, and how do you make it O(n)?",
      [("O(n^2) time because LinkedList.get(i) traverses nodes from the head/tail in O(i) time on every iteration", ["o(n^2)", "quadratic", "travers", "o(i)", "walk"], 2),
       ("use an enhanced for-each loop for (int x : list) (which uses an Iterator in O(1) per step) or use ArrayList", ["for (int", "for-each", "iterator", "arraylist", "o(n)"], 1.5)],
      [],
      "It runs in O(n^2) time. Unlike `ArrayList`, a `LinkedList` has no contiguous backing array, so each "
      "`list.get(i)` walks up to `i` nodes from the end of the list (`1 + 2 + ... + n/2 = O(n^2)`). Replace the "
      "indexed loop with `for (int x : list) total += x;`, which advances a single `Iterator` node by node in O(n) time."),

    Q("edge_cases_testing", "advanced", J, "Math.abs(Integer.MIN_VALUE) is still negative",
      """static int bucket(String s, int numBuckets) {
    return Math.abs(s.hashCode()) % numBuckets;
}""",
      "For which s.hashCode() value does bucket throw ArrayIndexOutOfBoundsException when used to index an array, why, and what is the safe fix?",
      [("when s.hashCode() == Integer.MIN_VALUE (-2147483648), Math.abs(Integer.MIN_VALUE) overflows and returns Integer.MIN_VALUE (still negative), making % negative", ["min_value", "-2147483648", "still negative", "negative"], 2),
       ("fix: use Math.floorMod(s.hashCode(), numBuckets) or (s.hashCode() & 0x7fffffff) % numBuckets", ["floormod", "0x7fffffff"], 1.5)],
      [],
      "When `s.hashCode()` is `Integer.MIN_VALUE` (`-2147483648`), its positive counterpart `+2147483648` cannot fit "
      "in a 32-bit signed `int` (max `2147483647`), so `Math.abs(Integer.MIN_VALUE)` overflows and returns "
      "`-2147483648`, and `% numBuckets` produces a negative index. Fix it with "
      "`Math.floorMod(s.hashCode(), numBuckets)` or `(s.hashCode() & 0x7fffffff) % numBuckets`."),

    Q("code_review_design", "advanced", J, "Overriding equals() without overriding hashCode()",
      """public final class UserId {
    private final long id;
    public UserId(long id) { this.id = id; }

    @Override
    public boolean equals(Object o) {
        return (o instanceof UserId u) && this.id == u.id;
    }
}""",
      "What bug occurs when UserId instances are placed in a HashSet or used as HashMap keys, and how do you fix UserId?",
      [("two equal UserId(42) objects have different default Object.hashCode() values, so HashSet/HashMap puts them in different buckets and fails to deduplicate or find them", ["hashcode", "bucket", "hashset", "hashmap", "contract"], 2),
       ("override public int hashCode() { return Long.hashCode(id); } (or Objects.hash(id), or declare public record UserId(long id) {})", ["long.hashcode", "objects.hash", "record", "override"], 1.5)],
      [],
      "`UserId` violates Java's `equals`/`hashCode` contract: equal objects must have equal hash codes. Because "
      "`hashCode()` is not overridden, `new UserId(42)` inherits `Object.hashCode()` (identity-based), so two equal "
      "`UserId(42)` instances hash to different buckets in a `HashSet` or `HashMap`. Override `hashCode()` to return "
      "`Long.hashCode(id)` (or define `public record UserId(long id) {}`)."),

    Q("data_structures", "advanced", J, "Top K largest numbers from a stream using PriorityQueue",
      """PriorityQueue<Integer> minHeap = new PriorityQueue<>(k);
for (int x : stream) {
    if (minHeap.size() < k) {
        minHeap.offer(x);
    } else if (x > minHeap.peek()) {
        minHeap.poll();
        minHeap.offer(x);
    }
}""",
      "Why do we use a min-heap (Java's default PriorityQueue) instead of a max-heap to keep the k largest elements, and what are the time and space complexities?",
      [("the smallest of the k largest candidates sits at the root (minHeap.peek()) in O(1), so we can compare x > peek() and evict the weakest candidate in O(log k)", ["smallest of the k", "peek", "evict", "root", "min-heap"], 2),
       ("O(n log k) time and O(k) space", ["o(n log k)", "n log k", "o(k)"], 1.5)],
      [],
      "Keeping the `k` largest elements seen so far requires quickly checking and evicting the *smallest* among those "
      "`k` elements whenever a bigger number arrives. A min-heap of size `k` keeps that threshold element at "
      "`minHeap.peek()` in O(1) time and replaces it in O(log k) time, giving O(n log k) total time and O(k) memory."),

    Q("algorithms", "advanced", J, "Longest substring without repeating characters in Java",
      """static int longestUnique(String s) {
    Map<Character, Integer> last = new HashMap<>();
    int left = 0, best = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        if (last.containsKey(c)) {
            left = Math.max(left, last.get(c) + 1);
        }
        last.put(c, right);
        best = Math.max(best, right - left + 1);
    }
    return best;
}""",
      "Why is left = Math.max(left, last.get(c) + 1) needed instead of left = last.get(c) + 1? Give an example input.",
      [("without Math.max, a character whose previous occurrence was before left (outside the current window) would move left backwards and re-include an earlier duplicate (e.g. \"abba\")", ["abba", "backwards", "before left", "outside the window"], 2),
       ("sliding window runs in O(n) time because right and left only move forward", ["o(n)", "only move forward", "sliding window"], 1.5)],
      [],
      "On `\"abba\"`, after seeing the second `'b'` at index 2, `left` advances to 2. When `'a'` is seen at index 3, "
      "`last.get('a')` is 0 (which is *before* `left = 2`); setting `left = 0 + 1 = 1` would move `left` backwards "
      "and include both `'b'`s in `\"bba\"`. `Math.max(left, last.get(c) + 1)` ensures `left` never moves left, "
      "keeping the window valid in O(n) time."),
]
