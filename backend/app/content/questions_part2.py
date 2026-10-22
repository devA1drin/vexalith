"""Seed questions: Edge Cases & Testing, Code Review & Design, Data Structures."""

from app.content.qdef import Q

QUESTIONS_PART2 = [
    # ── Edge cases & testing ─────────────────────────────────────────────────
    Q("edge_cases_testing", "beginner", "python", "Safe divide?",
      """def safe_divide(a, b):
    return a / b""",
      "List the edge cases you would test and what you expect for each.",
      [("division by zero", ["zero", "zerodivisionerror", "b = 0", "b=0"], 2), ("non-numeric / None inputs", ["string", "none", "type"], 1),
       ("floating-point results/precision", ["float", "precision", "decimal"], 1), ("negative numbers", ["negative"], 1)],
      [],
      "b = 0 (ZeroDivisionError — decide: raise, return None, or inf?), non-numeric inputs like '4' or None (TypeError), negatives, floats (0.1 / 0.3 precision), very large/small values. The name 'safe' implies zero is handled, but it isn't."),
    Q("edge_cases_testing", "beginner", "python", "Initials",
      """def initials(full_name):
    parts = full_name.split(" ")
    return parts[0][0] + parts[1][0]""",
      "Which inputs break this? Write down test cases.",
      [("single-word name → IndexError", ["single", "one word", "only one name", "indexerror", "one name"], 2), ("empty string", ["empty"], 1),
       ("extra/leading spaces", ["multiple spaces", "double space", "extra space", "leading", "trailing", "split()"], 1), ("middle names / three parts", ["middle", "three"], 1)],
      [],
      "Tests: 'Ada' (IndexError), '' (IndexError), 'Ada  Lovelace' (double space → empty part → IndexError), ' Ada Lovelace' (leading space), 'Ada King Lovelace' (middle name ignored?), lowercase names. Use split() without an argument and define behaviour for 1 or 3+ parts."),
    Q("edge_cases_testing", "beginner", "javascript", "Capitalize",
      """function capitalize(word) {
  return word[0].toUpperCase() + word.slice(1);
}""",
      "Which edge cases should tests cover? What happens for each?",
      [("empty string → word[0] is undefined → TypeError", ["empty", '""', "''"], 2), ("TypeError on undefined", ["undefined", "typeerror"], 1),
       ("non-string input (null, number)", ["null", "number", "non-string", "not a string"], 1), ("unicode / emoji", ["unicode", "emoji", "surrogate"], 1)],
      [],
      "'' → word[0] is undefined → TypeError; null/undefined/123 → TypeError; already-capitalised and all-caps words; leading space; emoji or astral characters (word[0] is half a surrogate pair); locale-specific letters (Turkish i)."),
    Q("edge_cases_testing", "beginner", "javascript", "Pagination",
      """function getPage(items, page, size) {
  const start = page * size;
  return items.slice(start, start + size);
}""",
      "Design test cases around the boundaries of this function.",
      [("negative page slices from the end", ["negative"], 2), ("last partial page", ["last page", "partial", "fewer"], 1), ("page beyond range → empty", ["beyond", "out of range", "past the end", "empty array", "empty"], 1),
       ("0- vs 1-indexed pages", ["0-indexed", "zero-indexed", "1-indexed", "page 0", "first page", "one-indexed"], 1)],
      [],
      "Page 0 vs 1 (is the API 0-indexed?), exact multiple vs partial last page, page past the end (returns [] — fine?), negative page (slice with negative start returns items from the end!), size 0 or negative, non-integer page values."),

    Q("edge_cases_testing", "intermediate", "python", "Testing parse_age",
      """def parse_age(text: str) -> int:
    age = int(text)
    if age < 0 or age > 150:
        raise ValueError("age out of range")
    return age""",
      "Write (or describe) a focused set of pytest cases for this function.",
      [("boundary values 0, 150, -1, 151", ["boundar", "151", "-1", "150"], 2), ("non-numeric input raises ValueError", ["abc", "non-numeric", "not a number", "valueerror"], 1),
       ("whitespace / decimal strings", ["whitespace", "42.5", "float", "decimal", "' 42 '", "space"], 1), ("assert exceptions with pytest.raises", ["pytest.raises", "assertraises", "raises"], 1)],
      [],
      "Valid: '0', '150', '42', ' 42 ' (int() strips whitespace). Invalid: '-1', '151' (out of range), 'abc', '', '42.5' (ValueError from int). Use pytest.mark.parametrize and `with pytest.raises(ValueError)`."),
    Q("edge_cases_testing", "intermediate", "python", "Merging intervals",
      """def merge_intervals(intervals):
    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged""",
      "List edge cases that would expose bugs or surprising behaviour.",
      [("empty input → IndexError", ["empty", "indexerror"], 2), ("touching intervals [1,2],[2,3]", ["touch", "adjacent", "[1, 2], [2, 3]", "[1,2],[2,3]"], 1),
       ("nested/contained intervals", ["nested", "contained", "inside"], 1), ("tuples are immutable → TypeError", ["tuple"], 1), ("mutates the caller's list", ["mutat", "in place", "sorts the input", "modifies"], 1)],
      [],
      "[] → IndexError; single interval; touching [1,2],[2,3] (merged — intended?); nested [1,10],[2,3]; unsorted input; tuples (item assignment TypeError); input list is sorted in place and inner lists are aliased into the result."),
    Q("edge_cases_testing", "intermediate", "javascript", "Parsing prices",
      """function parsePrice(input) {
  return Math.round(parseFloat(input) * 100) / 100;
}""",
      "Which inputs produce wrong or surprising results?",
      [("non-numeric gives NaN", ["nan"], 2), ("parseFloat is lenient ('12abc' → 12)", ["12abc", "partial", "lenient", "trailing"], 1),
       ("thousands separators ('1,234.50' → 1)", ["1,234", "comma", "thousand"], 1), ("binary floating-point rounding (1.005)", ["1.005", "floating", "binary", "precision"], 1)],
      [],
      "'abc' and '' → NaN; '12abc' → 12 silently; '1,234.50' → 1; '$5' → NaN; 1.005 rounds to 1 (binary float); negatives and '-0'. Prefer strict validation and integer cents."),
    Q("edge_cases_testing", "intermediate", "javascript", "Days between dates",
      """function daysBetween(a, b) {
  return (b - a) / (1000 * 60 * 60 * 24);
}""",
      "What edge cases would you test?",
      [("daylight-saving transitions", ["dst", "daylight"], 2), ("time zones / UTC", ["time zone", "timezone", "utc"], 1), ("argument order → negative", ["negative", "order"], 1),
       ("fractional days / rounding", ["fraction", "non-integer", "decimal", "math.round", "floor"], 1), ("invalid dates → NaN", ["invalid", "nan"], 1)],
      [],
      "DST changes make a 'day' 23/25 hours → fractional results; times of day; local vs UTC; a after b (negative); invalid Date → NaN; leap days. Normalise to UTC midnight and round."),

    Q("edge_cases_testing", "advanced", "python", "Dedupe with properties",
      """def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out""",
      "Design a test strategy including property-based tests. What invariants hold, and which inputs are tricky?",
      [("invariants / property-based testing (Hypothesis)", ["invariant", "property", "hypothesis", "idempoten"], 2), ("preserves first-occurrence order", ["order", "first occurrence"], 1),
       ("unhashable items raise TypeError", ["unhashable", "typeerror", "list of lists", "dict"], 1), ("1, 1.0 and True are equal and collapse", ["true", "1.0", "equal hash", "== 1"], 1)],
      [],
      "Properties: no duplicates in output; set(out) == set(items); out preserves first-occurrence order; dedupe(dedupe(x)) == dedupe(x). Use Hypothesis to generate lists. Tricky: unhashable elements (TypeError), 1 / 1.0 / True collapse, NaN (nan != nan but same object hashing), empty input."),
    Q("edge_cases_testing", "advanced", "python", "Testing time-dependent code",
      """from datetime import datetime

def is_expired(token):
    return token["expires_at"] < datetime.now()""",
      "How would you test this reliably? What edge cases matter?",
      [("control time: inject a clock / freezegun / mock", ["inject", "freezegun", "mock", "patch", "clock", "now parameter", "time-machine"], 2),
       ("naive vs aware datetimes / timezones", ["naive", "aware", "timezone", "utc"], 2), ("boundary when exactly equal", ["equal", "boundary", "exactly"], 1), ("missing key", ["keyerror", "missing"], 1)],
      [],
      "Make time controllable (pass `now` in, or use freezegun/time-machine). Test just before, exactly at (not expired with <) and after expiry. Comparing aware and naive datetimes raises TypeError; use timezone-aware UTC everywhere. Missing 'expires_at' → KeyError."),
    Q("edge_cases_testing", "advanced", "javascript", "Retry logic",
      """async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url);
    } catch (e) {
      if (i === retries - 1) throw e;
    }
  }
}""",
      "What behaviours are untested or wrong? Describe the tests you'd write.",
      [("HTTP 500 doesn't reject, so it isn't retried", ["500", "response.ok", "res.ok", "http error", "status"], 2), ("retries = 0 returns undefined", ["retries = 0", "retries=0", "undefined", "zero"], 1),
       ("no backoff between attempts", ["backoff", "delay", "wait"], 1), ("mock fetch / fake timers in tests", ["mock", "stub", "fake", "jest", "vi."], 1)],
      [],
      "fetch only rejects on network errors; a 500/503 resolves and is returned without retry. retries = 0 skips the loop and returns undefined. No backoff/jitter. Tests: mock fetch to fail N times then succeed, return 500s, assert call counts, use fake timers once backoff exists."),
    Q("edge_cases_testing", "advanced", "javascript", "Slugify",
      """function slugify(title) {
  return title.toLowerCase().replace(/ /g, "-");
}""",
      "Enumerate edge cases and expected outputs you'd assert.",
      [("multiple/leading/trailing spaces → '--' or leading '-'", ["multiple spaces", "double", "leading", "trailing", "--"], 2), ("punctuation and symbols", ["punctuation", "special character", "symbol"], 1),
       ("unicode/accents", ["unicode", "accent", "diacritic", "normalize", "é"], 1), ("tabs/newlines aren't replaced", ["tab", "newline", "\\s"], 1)],
      [],
      "'Hello  World' → 'hello--world'; ' Hi ' → '-hi-'; 'C++ & Rust!' keeps symbols; 'Crème brûlée' keeps accents; tabs/newlines untouched; '' → ''. Normalise (NFKD), strip non [a-z0-9], collapse whitespace/dashes, trim."),

    # ── Code review & design ─────────────────────────────────────────────────
    Q("code_review_design", "beginner", "python", "Review: calc",
      """def calc(l):
    r = []
    for i in range(len(l)):
        if l[i] > 0:
            r.append(l[i] * 2)
    return r""",
      "Review this function for readability. What would you change and why?",
      [("descriptive names", ["name", "rename", "descriptive"], 2), ("iterate directly / list comprehension", ["comprehension", "iterate directly", "for x in", "range(len"], 2),
       ("`l` is easily confused with 1/I (PEP 8)", ["l looks like", "ambiguous", "pep 8", "pep8", "confused with 1"], 1)],
      [],
      "Rename to describe intent (e.g. `double_positives(values)`), avoid `l` (PEP 8: looks like 1), iterate values directly and use a comprehension: `return [v * 2 for v in values if v > 0]`, add a docstring/type hints."),
    Q("code_review_design", "beginner", "python", "Review: discounts",
      """def get_discount(user_type):
    if user_type == "gold":
        return 0.2
    elif user_type == "silver":
        return 0.1
    elif user_type == "bronze":
        return 0.05
    else:
        return 0""",
      "Suggest improvements and explain the risks in the current version.",
      [("use a dict/mapping lookup", ["dict", "mapping", "lookup table"], 2), ("magic strings → Enum/constants", ["enum", "constant", "magic"], 1),
       ("unknown/typo inputs silently get 0", ["unknown", "typo", "invalid", "silently"], 2)],
      [],
      "Use a mapping `DISCOUNTS = {Tier.GOLD: 0.2, ...}` with an Enum instead of magic strings. Decide explicitly what unknown tiers do — today a typo like 'Gold' silently yields 0, hiding bugs; raise or log."),
    Q("code_review_design", "beginner", "javascript", "Review: process",
      """function process(data) {
  var result = [];
  for (var i = 0; i < data.length; i++) {
    if (data[i].active == true) {
      result.push(data[i].email);
    }
  }
  return result;
}""",
      "Review this code. What would you change?",
      [("const/let instead of var", ["const", "let"], 1), ("use === (or just the boolean)", ["===", "strict equality", "loose"], 1), ("filter/map instead of manual loop", ["filter", "map"], 2),
       ("better naming", ["name", "rename", "descriptive"], 1)],
      [],
      "Name it for intent (`activeUserEmails`), use const/let, avoid `== true` (just `u.active`), and express it declaratively: `users.filter(u => u.active).map(u => u.email)`."),
    Q("code_review_design", "beginner", "javascript", "Review: nested ifs",
      """function saveUser(user) {
  if (user) {
    if (user.email) {
      if (user.email.includes("@")) {
        db.save(user);
        return true;
      } else { return false; }
    } else { return false; }
  } else { return false; }
}""",
      "How would you restructure this, and what's missing?",
      [("guard clauses / early returns to flatten nesting", ["guard", "early return", "flatten", "nesting", "nested"], 2), ("validation is weak", ["validat", "regex", "@"], 1),
       ("boolean return hides the failure reason", ["error", "throw", "reason", "exception"], 1)],
      [],
      "Use guard clauses: `if (!user?.email?.includes('@')) return false;` then save. Consider throwing/returning a specific error so callers know why it failed, and move validation into its own function."),

    Q("code_review_design", "intermediate", "python", "Review: Report.build",
      """class Report:
    def __init__(self, data):
        self.data = data

    def build(self):
        rows = [f"{k}: {v}" for k, v in self.data.items()]
        text = "\\n".join(rows)
        with open("report.txt", "w") as f:
            f.write(text)
        send_email("boss@example.com", text)
        return text""",
      "Critique the design. Which principles does it violate, and how would you restructure it?",
      [("violates single responsibility (format + write + email)", ["single responsibility", "srp", "too many", "does too much", "responsibilit"], 2),
       ("hard-coded path and recipient", ["hard-coded", "hardcoded", "hard coded"], 1), ("hard to test; inject dependencies", ["test", "inject", "dependency"], 2)],
      [],
      "build() formats, writes a file and sends email — three reasons to change (SRP). Path and recipient are hard-coded, and side effects make it hard to unit test. Split into render() returning text, and separate writer/notifier objects injected by the caller."),
    Q("code_review_design", "intermediate", "python", "Review: find_user",
      """def find_user(users, email):
    try:
        return [u for u in users if u["email"] == email][0]
    except:
        return None""",
      "What are the problems with this implementation?",
      [("bare except swallows unrelated errors (KeyError, typos)", ["bare except", "except:", "catches everything", "swallow", "hides"], 2), ("use next() with a generator", ["next(", "generator"], 2),
       ("builds the whole list even after a match", ["whole list", "entire list", "all users", "efficien"], 1)],
      [],
      "The bare `except:` hides real bugs (a user missing 'email' → KeyError → silently None; even KeyboardInterrupt). It builds the full list before taking [0]. Use `next((u for u in users if u.get('email') == email), None)`."),
    Q("code_review_design", "intermediate", "javascript", "Review: Shape.area",
      """class Shape {
  area() {
    if (this.type === "circle") return Math.PI * this.r ** 2;
    if (this.type === "square") return this.side ** 2;
    if (this.type === "triangle") return 0.5 * this.b * this.h;
  }
}""",
      "Which design principle is strained here? Propose a better structure.",
      [("Open/Closed principle: adding a shape edits this method", ["open/closed", "open-closed", "open closed", "ocp"], 2), ("polymorphism: subclasses override area()", ["polymorph", "subclass", "override", "each shape"], 2),
       ("unknown type silently returns undefined", ["undefined", "unknown type", "default"], 1)],
      [],
      "Every new shape requires modifying area() (violates Open/Closed) and type strings are error-prone. Use polymorphism: Circle, Square, Triangle each implement area(). Today an unknown type returns undefined silently."),
    Q("code_review_design", "intermediate", "javascript", "Review: dashboard loading",
      """async function getDashboard(userId) {
  const user = await api.getUser(userId);
  const orders = await api.getOrders(userId);
  const messages = await api.getMessages(userId);
  return { user, orders, messages };
}""",
      "This page is slow. Review the code and suggest improvements.",
      [("independent requests run sequentially", ["sequential", "one after another", "waterfall", "serial"], 2), ("use Promise.all to run them concurrently", ["promise.all", "parallel", "concurrent"], 2),
       ("decide on partial-failure handling (allSettled)", ["allsettled", "error", "fail"], 1)],
      [],
      "The three calls are independent but awaited one after another (a waterfall), so latency adds up. Use `const [user, orders, messages] = await Promise.all([...])`. Decide whether one failure should fail the page or use Promise.allSettled for partial data."),

    Q("code_review_design", "advanced", "python", "Review: get_orders",
      """def get_orders(db, user_id, status):
    query = f"SELECT * FROM orders WHERE user_id = {user_id} AND status = '{status}'"
    return db.execute(query).fetchall()""",
      "Review this for security and maintainability.",
      [("SQL injection via string formatting", ["injection"], 3), ("use parameterized queries / bind parameters", ["parameter", "placeholder", "bind"], 2),
       ("avoid SELECT * — list explicit columns", ["select *", "explicit columns", "specific columns"], 1)],
      [],
      "Interpolating `status` into SQL allows injection (status = \"x' OR '1'='1\"). Use parameterized queries: `db.execute('SELECT id, total FROM orders WHERE user_id = %s AND status = %s', (user_id, status))`. Select explicit columns and consider pagination."),
    Q("code_review_design", "advanced", "python", "Review: rate cache",
      """_cache = {}

def get_exchange_rate(currency):
    if currency not in _cache:
        _cache[currency] = fetch_rate_from_api(currency)
    return _cache[currency]""",
      "What tradeoffs and risks does this cache introduce? How would you improve it?",
      [("rates never expire → stale data (needs TTL)", ["stale", "ttl", "expire", "expiry", "invalidat"], 2), ("unbounded growth", ["unbounded", "memory", "grow"], 1),
       ("global state hurts testability", ["global", "test"], 1), ("concurrency / thundering herd", ["thread", "concurren", "race", "herd"], 1)],
      [],
      "Exchange rates change, but entries never expire → stale prices; add a TTL. Keys come from input so the dict can grow unbounded (validate currencies / LRU). Module-level state is hard to reset in tests; concurrent misses can trigger duplicate API calls."),
    Q("code_review_design", "advanced", "javascript", "Review: formatPrice",
      """// utils.js — used across the app
export function formatPrice(cents, currency = "USD") {
  return "$" + (cents / 100).toFixed(2);
}""",
      "Review this shared utility.",
      [("currency parameter is ignored", ["ignore", "unused", "never used", "currency param"], 2), ("use Intl.NumberFormat", ["intl", "numberformat", "tolocalestring"], 2), ("locale-aware formatting", ["locale"], 1)],
      [],
      "The `currency` argument is silently ignored — formatPrice(500, 'EUR') shows '$5.00', a dangerous lie. Use `new Intl.NumberFormat(locale, { style: 'currency', currency }).format(cents / 100)` and respect currencies with 0 or 3 decimals."),
    Q("code_review_design", "advanced", "javascript", "Review: OrderService",
      """class OrderService {
  constructor() {
    this.db = new PostgresClient(process.env.DB_URL);
    this.mailer = new SmtpMailer();
  }
  async placeOrder(order) {
    await this.db.insert("orders", order);
    await this.mailer.send(order.email, "Thanks!");
  }
}""",
      "Critique the design (SOLID, testability, failure modes).",
      [("depends on concretions: inject dependencies (DIP)", ["dependency inversion", "dependency injection", "inject", "constructor parameter", "pass in"], 2), ("hard to unit test", ["test", "mock"], 1),
       ("mail failure after insert: retries/outbox/queue", ["fail", "retry", "queue", "outbox", "transaction"], 2)],
      [],
      "The service constructs concrete Postgres and SMTP clients (violates Dependency Inversion) so tests can't substitute fakes — inject interfaces via the constructor. If email fails after the insert, the caller sees an error although the order exists; send email asynchronously (queue/outbox) with retries."),

    # ── Data structures ─────────────────────────────────────────────────────
    Q("data_structures", "beginner", "python", "Banned words",
      """banned = ["spam", "scam", "phish"]  # will grow to 100k words

def is_banned(word):
    return word in banned""",
      "Which data structure should `banned` be, and why?",
      [("use a set", ["set"], 2), ("O(1) vs O(n) membership", ["o(1)", "o(n)", "constant", "linear"], 2), ("hash-based lookup", ["hash"], 1)],
      [],
      "`in` on a list is a linear scan (O(n)); with 100k words that's slow on a hot path. A set (hash table) gives O(1) average membership: `banned = {...}` or `frozenset(...)`."),
    Q("data_structures", "beginner", "python", "Stack operations",
      """stack = []
stack.append(1)
stack.append(2)
stack.append(3)
print(stack.pop(), stack.pop(0), stack)""",
      "What is printed? Comment on the cost of each pop.",
      [("prints 3 1 [2]", ["3 1 [2]", "3, 1, [2]"], 2), ("pop() takes from the end (LIFO)", ["lifo", "last in", "end"], 1), ("pop(0) is O(n); use deque for queues", ["o(n)", "deque", "shift"], 1)],
      [],
      "It prints `3 1 [2]`. pop() removes the last element (LIFO, O(1)); pop(0) removes the first and shifts the rest (O(n)) — use collections.deque for queue behaviour."),
    Q("data_structures", "beginner", "javascript", "Map vs object keys",
      """const m = new Map();
m.set("1", "string key");
m.set(1, "number key");
const o = {};
o["1"] = "string key";
o[1] = "number key";
console.log(m.size, Object.keys(o).length);""",
      "What is logged and why do the two differ?",
      [("logs 2 1", ["2 1", "2, 1"], 2), ("object keys are coerced to strings", ["coerc", "string", "converted"], 2), ("Map keeps key types distinct", ["map keeps", "any type", "key type", "distinct", "different keys"], 1)],
      [],
      "It logs `2 1`. Map keys keep their type, so '1' and 1 are distinct. Plain-object property keys are converted to strings, so o[1] overwrites o['1']."),
    Q("data_structures", "beginner", "javascript", "Queue or stack?",
      """const queue = [];
queue.push("a"); queue.push("b"); queue.push("c");
console.log(queue.shift(), queue.pop(), queue);""",
      "Predict the output and explain which end each method uses.",
      [("logs a c", ["a c", "a, c"], 2), ("shift takes the front, pop the end", ["front", "fifo", "beginning", "first"], 1), ("remaining ['b']", ["['b']", '["b"]', "[ 'b' ]", "only b"], 1)],
      [],
      "Output: `a c [ 'b' ]`. shift() removes from the front (FIFO), pop() from the end (LIFO), leaving ['b']."),

    Q("data_structures", "intermediate", "python", "Word counts",
      """words = "the cat and the hat and the bat".split()
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1
top = max(counts, key=counts.get)
print(top, counts[top])""",
      "What is printed? Explain the dictionary usage and an idiomatic alternative.",
      [("prints the 3", ["the 3", "the, 3"], 2), ("hash map counting with get(default)", ["dict", "hash", "get("], 1), ("collections.Counter / most_common", ["counter", "most_common"], 1)],
      [],
      "It prints `the 3`. The dict maps word → count (get(w, 0) supplies a default), and max with key=counts.get returns the key with the highest count. Idiomatic: `Counter(words).most_common(1)`."),
    Q("data_structures", "intermediate", "python", "Priority tasks",
      """tasks = []

def add_task(priority, name):
    tasks.append((priority, name))
    tasks.sort()

def next_task():
    return tasks.pop(0)""",
      "Tasks arrive constantly. Evaluate this and choose a better structure.",
      [("use a heap / priority queue (heapq)", ["heap", "heapq", "priority queue"], 2), ("push/pop become O(log n)", ["log n"], 2), ("current cost: sort each add + pop(0) O(n)", ["n log n", "o(n)", "sort every", "pop(0)"], 1)],
      [],
      "Re-sorting on every add costs O(n log n) and pop(0) is O(n). A binary heap (heapq.heappush / heappop) gives O(log n) for both while always exposing the smallest priority."),
    Q("data_structures", "intermediate", "javascript", "Spread copies",
      """const a = { x: 1, nested: { y: 2 } };
const b = { ...a };
b.x = 10;
b.nested.y = 20;
console.log(a.x, a.nested.y);""",
      "What is logged? Explain the copy semantics.",
      [("logs 1 20", ["1 20", "1, 20"], 2), ("spread is a shallow copy", ["shallow"], 2), ("deep clone with structuredClone", ["structuredclone", "deep copy", "deep clone"], 1)],
      [],
      "It logs `1 20`. Spread creates a shallow copy: x is copied by value, but nested still references the same object. Use structuredClone(a) for a deep copy."),
    Q("data_structures", "intermediate", "javascript", "Visited list",
      """const visited = [];
function visit(node) {
  if (visited.includes(node.id)) return;
  visited.push(node.id);
  node.children.forEach(visit);
}""",
      "What's the complexity problem here and how do you fix it?",
      [("use a Set for visited", ["set"], 2), ("includes makes traversal O(n^2)", ["o(n^2)", "o(n²)", "quadratic"], 2), ("Set.has is O(1)", ["o(1)", "has(", "constant"], 1)],
      [],
      "includes() is O(n), called once per node → O(n²) traversal. Use `const visited = new Set()` with has/add for O(1) average, making the traversal O(V + E). (Also consider an explicit stack to avoid deep recursion.)"),

    Q("data_structures", "advanced", "python", "LRU cache with a list",
      """class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []  # list of (key, value)

    def get(self, key):
        for i, (k, v) in enumerate(self.items):
            if k == key:
                self.items.append(self.items.pop(i))
                return v
        return None
    # put(): similar linear scan; evicts self.items.pop(0)""",
      "Analyse the complexity and redesign for O(1) operations.",
      [("current get/put are O(n)", ["o(n)", "linear"], 1), ("hash map + doubly linked list / OrderedDict.move_to_end", ["ordereddict", "linked list", "move_to_end"], 2), ("O(1) get and put", ["o(1)", "constant"], 2)],
      [],
      "Every operation scans the list (O(n)) and pop(i)/pop(0) shift elements. Combine a dict (key → node) with a doubly linked list for recency, or use OrderedDict with move_to_end() and popitem(last=False): O(1) get/put."),
    Q("data_structures", "advanced", "python", "Autocomplete",
      """words = load_dictionary()  # 500k words

def autocomplete(prefix):
    return [w for w in words if w.startswith(prefix)][:10]""",
      "This is called on every keystroke. Propose a better data structure and analyse it.",
      [("trie / prefix tree", ["trie", "prefix tree"], 2), ("or sorted list + binary search (bisect)", ["bisect", "binary search", "sorted"], 2), ("current cost scans every word", ["o(n", "linear", "every word", "scans"], 1)],
      [],
      "Each call scans all 500k words (O(n·p)) and builds a full list before slicing. A trie finds the prefix node in O(p) and walks only matching words; alternatively keep words sorted and use bisect to find the first match in O(log n), then take 10."),
    Q("data_structures", "advanced", "javascript", "Undo/redo",
      """const history = [];
let index = -1;
function record(state) {
  history.push(state);
  index++;
}
function undo() { return history[--index]; }
function redo() { return history[++index]; }""",
      "Find the logical bugs and propose a sound data-structure design.",
      [("recording after undo must discard the redo branch", ["truncat", "discard", "redo stack", "splice", "branch", "length = index"], 2), ("no bounds checks", ["bound", "negative", "undefined", "out of range"], 1),
       ("two stacks (undo/redo)", ["two stacks", "stack"], 1), ("memory: cap history or store diffs", ["memory", "diff", "limit", "cap"], 1)],
      [],
      "After undo, record() appends at the end instead of truncating the redo branch, so index points at the wrong state. undo/redo have no bounds (index goes −1/past end → undefined). Use two stacks (undo, redo; clear redo on new record) and cap size or store diffs."),
    Q("data_structures", "advanced", "javascript", "Social graph representation",
      """// 1,000,000 users, ~150 friends each
// Option A: adjacency matrix
const matrix = Array.from({ length: N }, () => new Uint8Array(N));
// Option B: adjacency list
const adj = new Map(); // userId -> Set of friendIds""",
      "Which representation would you choose and why? Quantify.",
      [("matrix needs N² ≈ 10^12 bytes (infeasible)", ["n^2", "n²", "10^12", "terabyte", "memory"], 2), ("graph is sparse", ["sparse"], 1), ("adjacency list with Sets (Option B)", ["adjacency list", "option b"], 2),
       ("Set gives O(1) edge checks", ["o(1)", "has("], 1)],
      [],
      "Option B. A matrix needs N² = 10¹² bytes (~1 TB) even as Uint8Array, while the graph is sparse (~1.5×10⁸ edges). Map<id, Set<id>> uses O(V + E) memory and still offers O(1) average edge checks via Set.has."),
]
