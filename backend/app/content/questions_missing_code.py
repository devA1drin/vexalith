"""Fill-in-the-missing-code drills for every language: read a real snippet, then supply the
line, expression, tag or property that replaces the ____ blank."""

from app.content.qdef import FB

F = "fundamentals"

QUESTIONS_MISSING_CODE = [
    # ── Python ──────────────────────────────────────────────────────────────
    FB(F, "beginner", "python", "Missing code: greet by name",
       """name = "Ada"
print(____)
# should print: Hello, Ada!""",
       "Fill in the blank so the program prints Hello, Ada!",
       ['f"Hello, {name}!"', '"Hello, " + name + "!"', '"Hello, {}!".format(name)', '"Hello, %s!" % name'],
       [("the value comes from the variable name, not typed in by hand", ["variable", "f-string", "concaten", "join"], 1)],
       [],
       "The blank is f\"Hello, {name}!\". An f-string puts the value of the variable name inside the text, so it "
       "prints Hello, Ada!. \"Hello, \" + name + \"!\" (concatenation) works too."),
    FB(F, "beginner", "python", "Missing code: count from 1 to 5",
       """for i in ____:
    print(i)
# should print 1, 2, 3, 4, 5 (one per line)""",
       "Fill in the blank so the loop prints the numbers 1 to 5.",
       ["range(1, 6)", "[1, 2, 3, 4, 5]", "(1, 2, 3, 4, 5)"],
       [("range stops before its end value, so the end must be 6", ["before", "not included", "excluded", "stops at"], 1)],
       [("uses range(1, 5)", ["range(1, 5)"], "range(1, 5) stops before 5, so it prints only 1 to 4."),
        ("uses range(5)", ["range(5)"], "range(5) gives 0 to 4.")],
       "The blank is range(1, 6). range starts at 1 and stops before its end value (the end is not included), so "
       "the end must be 6 to print 1 to 5."),
    FB(F, "intermediate", "python", "Missing code: return the larger number",
       """def bigger(a, b):
    if a > b:
        ____
    return b

print(bigger(7, 3))  # 7""",
       "Fill in the missing line so bigger returns the larger of the two numbers.",
       ["return a"],
       [("return ends the function immediately, so return b only runs when a > b is false", ["immediately", "ends the function", "exits", "stops the function", "only runs"], 1)],
       [("prints instead of returning", ["print(a)"], "print shows a value but the function would still return b; the caller needs return.")],
       "The missing line is return a. return ends the function immediately, so when a > b it gives back a, and the "
       "last line return b only runs when a > b is false. print(a) would not work: the function would still return "
       "b."),
    FB(F, "intermediate", "python", "Missing code: count the vowels",
       """word = "banana"
count = 0
for ch in word:
    if ____:
        count += 1
print(count)  # 3""",
       "Fill in the condition so the loop counts the vowels in word.",
       ['ch in "aeiou"', 'ch in "aeiouAEIOU"', 'ch.lower() in "aeiou"', "ch in ['a', 'e', 'i', 'o', 'u']",
        'ch in "aeiouy"', "ch in {'a', 'e', 'i', 'o', 'u'}"],
       [("in checks whether the character is one of the vowels", ["one of", "membership", "contains", "checks whether"], 1)],
       [],
       "The condition is ch in \"aeiou\". The in operator checks whether the character is one of the letters in the "
       "string (membership), so the three a's are counted and it prints 3. Use ch.lower() in \"aeiou\" to also count "
       "capital vowels."),
    FB("algorithms", "advanced", "python", "Missing code: move the low end of a binary search",
       """def search(xs, target):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if xs[mid] == target:
            return mid
        elif xs[mid] < target:
            ____
        else:
            hi = mid - 1
    return -1""",
       "xs is sorted. Fill in the missing line and explain why it is correct.",
       ["lo = mid + 1"],
       [("the target can only be to the right of mid, so mid itself is excluded", ["right of mid", "right half", "to the right", "upper half", "excluded"], 1),
        ("the +1 guarantees progress; lo = mid could loop forever", ["forever", "infinite", "progress", "shrink"], 1)],
       [("sets lo = mid", ["lo = mid"], "Without + 1 the range may never shrink (e.g. lo = hi - 1) and the loop never ends.")],
       "The missing line is lo = mid + 1. Since xs is sorted and xs[mid] < target, the target can only be to the right "
       "of mid, and mid itself is excluded. The + 1 also guarantees progress: with lo = mid the range might never "
       "shrink and the loop could run forever."),
    FB("data_structures", "advanced", "python", "Missing code: count words in a dict",
       """words = ["to", "be", "or", "not", "to", "be"]
counts = {}
for w in words:
    counts[w] = ____
print(counts["to"], counts["or"])  # 2 1""",
       "Fill in the blank with one expression that works the first time a word is seen too.",
       ["counts.get(w, 0) + 1", "1 + counts.get(w, 0)"],
       [("get returns 0 for a missing key instead of raising KeyError", ["keyerror", "missing key", "default", "returns 0"], 1)],
       [("uses counts[w] + 1", ["counts[w] + 1"], "counts[w] raises KeyError the first time w is seen.")],
       "The blank is counts.get(w, 0) + 1. get returns the default 0 for a missing key instead of raising KeyError, "
       "so the first time a word is seen it becomes 1, and later times add one. collections.Counter(words) does the "
       "same in one step."),

    # ── JavaScript ──────────────────────────────────────────────────────────
    FB(F, "beginner", "javascript", "Missing code: build a full name",
       """const first = "Ada";
const last = "Lovelace";
const full = ____;
console.log(full); // Ada Lovelace""",
       "Fill in the blank so full is \"Ada Lovelace\".",
       ["`${first} ${last}`", 'first + " " + last', '[first, last].join(" ")', "first.concat(\" \", last)"],
       [("the space between the names must be added explicitly", ["space"], 1)],
       [],
       "The blank is `${first} ${last}`: a template literal puts both values into the text with a space between "
       "them. first + \" \" + last works too; the space must be added explicitly, or you get AdaLovelace."),
    FB(F, "beginner", "javascript", "Missing code: loop over every fruit",
       """const fruits = ["apple", "pear", "plum"];
for (let i = 0; ____; i++) {
  console.log(fruits[i]);
}""",
       "Fill in the loop condition so every fruit is printed exactly once.",
       ["i < fruits.length", "i <= fruits.length - 1", "fruits.length > i"],
       [("indexes go from 0 to length - 1", ["length - 1", "0 to", "last index"], 1)],
       [("uses i <= fruits.length", ["i <= fruits.length"], "i <= fruits.length runs once too many and prints undefined.")],
       "The condition is i < fruits.length. Indexes go from 0 to length - 1 (0 to 2 here), so the loop must stop when "
       "i reaches 3. i <= fruits.length would run once too many and print undefined."),
    FB(F, "intermediate", "javascript", "Missing code: keep the even numbers",
       """const nums = [1, 2, 3, 4, 5, 6];
const evens = nums.filter(____);
console.log(evens); // [2, 4, 6]""",
       "Fill in the function passed to filter.",
       ["n => n % 2 === 0", "(n) => n % 2 === 0", "x => x % 2 === 0", "(x) => x % 2 === 0", "n => n % 2 == 0",
        "x => x % 2 == 0", "n => !(n % 2)", "function (n) { return n % 2 === 0; }"],
       [("filter keeps the items for which the function returns true", ["returns true", "keeps", "true"], 1)],
       [],
       "The blank is n => n % 2 === 0. filter calls the function for each item and keeps the items for which it "
       "returns true; n % 2 === 0 is true for even numbers, so evens is [2, 4, 6] and nums is unchanged."),
    FB("code_tracing", "intermediate", "javascript", "Missing code: wait for the response",
       """async function loadUser() {
  const res = ____ fetch("/api/user");
  const user = await res.json();
  return user.name;
}""",
       "Fill in the missing keyword so res is the Response, not a Promise.",
       ["await"],
       [("fetch returns a Promise; await pauses the async function until it resolves", ["promise", "resolve", "pause", "wait"], 1)],
       [],
       "The missing keyword is await. fetch returns a Promise; await pauses the async function until it resolves, so "
       "res is the actual Response and res.json() works. Without it, res would be a Promise and res.json is not a "
       "function."),
    FB("algorithms", "advanced", "javascript", "Missing code: remember the result",
       """function fib(n, memo = new Map()) {
  if (n <= 1) return n;
  if (memo.has(n)) return memo.get(n);
  const v = fib(n - 1, memo) + fib(n - 2, memo);
  ____;
  return v;
}""",
       "Fill in the missing line so this runs in linear time. Why does it matter?",
       ["memo.set(n, v)"],
       [("storing each result means every n is computed once: O(n) instead of exponential", ["o(n)", "once", "exponential", "linear"], 1)],
       [],
       "The missing line is memo.set(n, v). Storing each result means every n is computed only once; later calls hit "
       "memo.has(n). That makes it O(n) (linear) instead of exponential, roughly O(2^n), without the memo."),
    FB("code_tracing", "advanced", "javascript", "Missing code: one i per iteration",
       """for (____ i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// should print 0, 1, 2""",
       "Fill in the keyword so the callbacks print 0, 1, 2. What would var print, and why?",
       ["let"],
       [("let creates a new binding of i for each iteration, which each callback captures", ["new binding", "each iteration", "block scope", "block-scoped", "captures"], 1),
        ("var has one shared i, which is 3 when the callbacks run: 3 3 3", ["3 3 3", "shared", "one i"], 1)],
       [("uses var", ["var"], "With var there is one function-scoped i, so all callbacks print 3.")],
       "The keyword is let. let is block-scoped and creates a new binding of i for each iteration, and each callback "
       "captures its own one, so it prints 0, 1, 2. With var there is one shared i that is already 3 when the "
       "callbacks run, so it prints 3 3 3."),

    # ── PHP ─────────────────────────────────────────────────────────────────
    FB(F, "beginner", "php", "Missing code: echo a greeting",
       """<?php
$name = "Sam";
____;
// should print: Hello, Sam!""",
       "Fill in the missing statement so it prints Hello, Sam!",
       ['echo "Hello, $name!"', 'echo "Hello, " . $name . "!"', 'echo "Hello, {$name}!"', 'print "Hello, $name!"',
        'printf("Hello, %s!", $name)'],
       [("double quotes insert the variable's value; single quotes would not", ["double quote", "insert", "interpolat", "single quote"], 1)],
       [("uses single quotes", ["echo 'hello, $name!'"], "Inside single quotes $name is printed literally.")],
       "The statement is echo \"Hello, $name!\". Inside double quotes PHP inserts (interpolates) the value of $name; "
       "single quotes would print $name literally. echo \"Hello, \" . $name . \"!\" also works."),
    FB(F, "beginner", "php", "Missing code: foreach over colours",
       """<?php
$colors = ["red", "green", "blue"];
foreach (____) {
    echo $c, "\\n";
}""",
       "Fill in the foreach header so each colour is printed on its own line.",
       ["$colors as $c", "$colors as $i => $c", "$colors as $key => $c"],
       [("the array comes first, then as and the variable used in the body", ["comes first", "array first", "then as", "body uses $c", "the body"], 1)],
       [],
       "The header is $colors as $c. The array comes first, then as and the variable name; the body uses $c, so it "
       "must be called $c. Each pass puts the next colour into $c."),
    FB(F, "intermediate", "php", "Missing code: check the key exists",
       """<?php
$user = ["name" => "Ana"];
if (____) {
    echo $user["email"];
} else {
    echo "no email";
}""",
       "Fill in the condition so there is no warning when the email key is missing.",
       ['isset($user["email"])', 'array_key_exists("email", $user)', '!empty($user["email"])'],
       [("reading a missing key gives Warning: Undefined array key; isset checks first", ["undefined array key", "warning", "checks first", "missing key"], 1)],
       [],
       "The condition is isset($user[\"email\"]). Reading a missing key gives Warning: Undefined array key, so isset "
       "checks first (it is also false for null). array_key_exists(\"email\", $user) is true even when the value is "
       "null."),
    FB(F, "intermediate", "php", "Missing code: return the sum",
       """<?php
function add(int $a, int $b): int {
    ____
}
echo add(2, 3); // 5""",
       "Fill in the body of add.",
       ["return $a + $b;", "return $b + $a;"],
       [("return gives the value back; echo inside the function would not satisfy the int return type", ["gives the value back", "give back", "return type", ": int"], 1)],
       [("echoes instead of returning", ["echo $a + $b"], "echo prints but returns nothing, which breaks the : int return type (TypeError).")],
       "The body is return $a + $b;. return gives the value back to the caller, which then echoes 5. echo inside "
       "the function would print but return nothing, which breaks the : int return type with a TypeError."),
    FB("code_review_design", "advanced", "php", "Missing code: run the prepared query",
       """<?php
$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
____;
$user = $stmt->fetch();""",
       "Fill in the missing line that runs the query with the user's $email. Why is this safer than building the SQL string?",
       ["$stmt->execute([$email])", "$stmt->execute(array($email))"],
       [("the value is bound to the ? placeholder, never pasted into the SQL, which prevents SQL injection", ["sql injection", "injection", "bound", "placeholder"], 1)],
       [],
       "The missing line is $stmt->execute([$email]). The value is bound to the ? placeholder and sent separately "
       "from the SQL text, never pasted into it, so a malicious email cannot change the query: that prevents SQL "
       "injection."),
    FB("algorithms", "advanced", "php", "Missing code: sort people by age",
       """<?php
$people = [["name" => "Bo", "age" => 41], ["name" => "Al", "age" => 29]];
usort($people, fn($a, $b) => ____);
echo $people[0]["name"]; // Al""",
       "Fill in the comparison so people are sorted by age, youngest first.",
       ['$a["age"] <=> $b["age"]', '$a["age"] - $b["age"]'],
       [("<=> returns -1, 0 or 1, which is what usort expects", ["-1, 0 or 1", "negative", "spaceship", "-1"], 1)],
       [("reverses the order", ['$b["age"] <=> $a["age"]'], "That sorts oldest first.")],
       "The blank is $a[\"age\"] <=> $b[\"age\"]. The spaceship operator <=> returns -1, 0 or 1 (negative when $a "
       "should come first), which is what usort expects, so the youngest, Al, ends up first. usort is O(n log n)."),

    # ── C++ ─────────────────────────────────────────────────────────────────
    FB(F, "beginner", "cpp", "Missing code: print the score",
       """#include <iostream>

int main() {
    int score = 42;
    ____ << "Score: " << score << '\\n';
}""",
       "Fill in the blank so the program prints Score: 42.",
       ["std::cout", "cout"],
       [("cout is the standard output stream and << sends each value to it", ["output stream", "standard output", "sends"], 1)],
       [("uses cin", ["std::cin", "cin"], "cin is for reading input; output goes to cout.")],
       "The blank is std::cout. cout is the standard output stream (the screen), and each << sends the next value to "
       "it, so it prints Score: 42. Plain cout works too after using namespace std;."),
    FB(F, "beginner", "cpp", "Missing code: read the age",
       """#include <iostream>

int main() {
    int age;
    std::cout << "Age? ";
    ____;
    std::cout << "In ten years: " << age + 10;
}""",
       "Fill in the missing statement so age holds the number the user types.",
       ["std::cin >> age", "cin >> age"],
       [(">> points from cin into the variable: the data flows into age", ["into age", "into the variable", "flows", "reads"], 1)],
       [("uses << with cin", ["cin << age"], "cin uses >>; the arrow points the way the data flows, into age.")],
       "The statement is std::cin >> age;. cin reads what the user types, and >> points from cin into the variable, "
       "so the data flows into age."),
    FB(F, "intermediate", "cpp", "Missing code: swap through references",
       """void swapInts(____ a, int& b) {
    int t = a;
    a = b;
    b = t;
}

int main() {
    int x = 1, y = 2;
    swapInts(x, y);
    std::cout << x << y;  // 21
}""",
       "Fill in the type of the first parameter so the swap changes x in main.",
       ["int&", "int &"],
       [("a reference makes a another name for x; a plain int would be a copy", ["another name", "reference", "copy", "alias"], 1)],
       [("uses plain int", ["(int a", "plain int"], "A plain int parameter is a copy, so x would stay 1.")],
       "The type is int&. A reference makes a another name (alias) for x, so assigning to a changes x. A plain int "
       "would be a copy and x would stay 1. (std::swap(x, y) does this for you.)"),
    FB(F, "intermediate", "cpp", "Missing code: double every element",
       """std::vector<int> v = {1, 2, 3};
for (____ : v) {
    x *= 2;
}
// v is now {2, 4, 6}""",
       "Fill in the loop variable so the vector itself is changed.",
       ["int& x", "auto& x", "int &x", "auto &x"],
       [("& makes x refer to each element; without it x is a copy", ["refer", "reference", "copy"], 1)],
       [("uses int x", ["int x"], "int x is a copy of each element, so v would not change.")],
       "The loop variable is int& x (or auto& x). The & makes x a reference to each element, so x *= 2 changes the "
       "vector itself. With int x, x is a copy and v would stay {1, 2, 3}."),
    FB("code_review_design", "advanced", "cpp", "Missing code: own it with a smart pointer",
       """struct Shape { virtual ~Shape() = default; virtual double area() const = 0; };
struct Circle : Shape {
    double r;
    explicit Circle(double r) : r(r) {}
    double area() const override { return 3.14159 * r * r; }
};

std::unique_ptr<Shape> shape = ____;   // a Circle of radius 2""",
       "Fill in the blank to create the Circle without writing new or delete. Why is this better?",
       ["std::make_unique<Circle>(2.0)", "make_unique<Circle>(2.0)", "std::make_unique<Circle>(2)", "make_unique<Circle>(2)"],
       [("unique_ptr deletes the Circle automatically when it goes out of scope (RAII), so there is no leak", ["automatically", "raii", "no leak", "leak", "out of scope"], 1)],
       [],
       "The blank is std::make_unique<Circle>(2.0). The unique_ptr owns the Circle and deletes it automatically when "
       "it goes out of scope (RAII), so there is no leak even if an exception is thrown, and there is no raw new or "
       "delete to get wrong."),
    FB("algorithms", "advanced", "cpp", "Missing code: sort largest first",
       """std::vector<int> v = {3, 9, 1, 7};
std::sort(v.begin(), v.end(), ____);
// v is now {9, 7, 3, 1}""",
       "Fill in the comparator so the vector is sorted in descending order.",
       ["std::greater<int>()", "std::greater<>()", "std::greater<int>{}", "std::greater<>{}", "greater<int>()",
        "[](int a, int b) { return a > b; }", "[](const int& a, const int& b) { return a > b; }",
        "[](auto a, auto b) { return a > b; }"],
       [("the comparator returns true when a should come before b", ["come before", "comes before", "before b", "returns true"], 1)],
       [],
       "The blank is std::greater<int>() (or a lambda [](int a, int b) { return a > b; }). sort's comparator returns "
       "true when a should come before b, so with > the larger values come first. Sorting stays O(n log n)."),

    # ── HTML ────────────────────────────────────────────────────────────────
    FB(F, "beginner", "html", "Missing code: the opening link tag",
       """<p>Read the ____docs</a> before you start.</p>
<!-- "docs" should link to /docs -->""",
       "Fill in the missing opening tag so the word docs links to /docs.",
       ['<a href="/docs">'],
       [("the a tag makes a link and href says where it goes", ["href", "where it goes", "link"], 1)],
       [("uses a link element", ["<link"], "<link> is for stylesheets in the head; clickable links use <a>.")],
       "The missing tag is <a href=\"/docs\">. The a (anchor) element makes a clickable link, and its href "
       "attribute says where it goes; the </a> already in the code closes it."),
    FB(F, "beginner", "html", "Missing code: describe the image",
       """<img src="cat.jpg" ____>
<!-- screen readers should announce: "A cat asleep on a sofa" -->""",
       "Fill in the missing attribute so screen-reader users know what the image shows.",
       ['alt="A cat asleep on a sofa"', "alt="],
       [("alt text is read aloud by screen readers and shown if the image fails to load", ["screen reader", "read aloud", "fails to load", "accessib"], 1)],
       [("uses title", ["title="], "title is a tooltip and is not a reliable text alternative; use alt.")],
       "The attribute is alt=\"A cat asleep on a sofa\". Alt text is read aloud by screen readers and shown if the "
       "image fails to load, which makes the page accessible."),
    FB(F, "intermediate", "html", "Missing code: connect the label",
       """<label ____>Email</label>
<input id="email" type="email" name="email">""",
       "Fill in the missing attribute so clicking the label focuses the input and screen readers read Email for it.",
       ['for="email"'],
       [("for must match the input's id", ["match", "same as the id", "the id"], 1)],
       [("uses name", ['name="email"'], "A label connects through for → id, not name.")],
       "The attribute is for=\"email\". A label's for must match the input's id, which links them: clicking the label "
       "focuses the input, and screen readers announce Email for it."),
    FB("code_review_design", "intermediate", "html", "Missing code: a field you can't skip",
       """<form action="/subscribe">
  <input type="email" name="email" ____>
  <button>Subscribe</button>
</form>""",
       "Fill in the missing attribute so the browser refuses to submit the form while the field is empty.",
       ["required"],
       [("the browser validates before submitting, but the server must still check", ["validate", "server", "before submit"], 1)],
       [],
       "The attribute is required. The browser then validates before submitting and shows a message if the field is "
       "empty (type=\"email\" also checks the format). The server must still check, because client-side validation "
       "can be bypassed."),

    # ── CSS ─────────────────────────────────────────────────────────────────
    FB(F, "beginner", "css", "Missing code: red paragraph text",
       """p {
  ____
}
/* the text of every paragraph should be red */""",
       "Fill in the missing declaration.",
       ["color: red;", "color: #f00;", "color: #ff0000;", "color: rgb(255, 0, 0);"],
       [("color sets the text colour; background-color would colour the box behind it", ["text colour", "text color", "background-color"], 1)],
       [("uses background-color", ["background-color"], "background-color paints behind the text, not the text itself.")],
       "The declaration is color: red;. The color property sets the text colour; background-color would paint the "
       "box behind the text instead. Each declaration is property: value; inside the braces."),
    FB(F, "beginner", "css", "Missing code: center horizontally with flexbox",
       """.box {
  display: flex;
  ____
  align-items: center;
}
/* the child should be centered left-to-right and top-to-bottom */""",
       "Fill in the missing declaration so the child is centered horizontally too.",
       ["justify-content: center;"],
       [("justify-content works along the main axis (a row by default); align-items along the cross axis", ["main axis", "cross axis", "row"], 1)],
       [("uses text-align", ["text-align"], "text-align centers inline text, not flex items.")],
       "The declaration is justify-content: center;. In a flex container justify-content works along the main axis "
       "(a row, left to right, by default) and align-items along the cross axis (top to bottom), so together they "
       "center the child."),
    FB(F, "intermediate", "css", "Missing code: space inside the border",
       """.card {
  border: 1px solid #ccc;
  ____
}
/* 16px of space between the border and the text inside */""",
       "Fill in the missing declaration.",
       ["padding: 16px;", "padding: 1rem;"],
       [("padding is inside the border; margin is outside it", ["inside the border", "outside", "margin"], 1)],
       [("uses margin", ["margin: 16px"], "margin adds space outside the border, between the card and its neighbours.")],
       "The declaration is padding: 16px;. In the box model padding is the space inside the border, between it and "
       "the content; margin is outside the border, between the card and its neighbours."),
    FB("code_tracing", "intermediate", "css", "Missing code: style on hover",
       """button____ {
  background: #111;
  color: #fff;
}
/* only while the mouse is over the button */""",
       "Fill in the missing part of the selector.",
       [":hover"],
       [("a pseudo-class with a single colon matches a state, not an element", ["pseudo-class", "state", "single colon"], 1)],
       [],
       "The missing part is :hover, so the selector is button:hover. A pseudo-class (one colon) matches a state of "
       "the element, here while the pointer is over it. Add :focus-visible too so keyboard users get the same cue."),

    # ── General (pseudocode algorithms) ─────────────────────────────────────
    FB("algorithms", "beginner", "general", "Missing code: keep the biggest so far",
       """best = first item of list
for each x in list:
    if ____:
        best = x
print best""",
       "Fill in the condition so best ends up as the largest item.",
       ["x > best", "best < x", "x >= best"],
       [("best always holds the largest value seen so far", ["so far", "largest seen", "seen so far"], 1)],
       [("compares the wrong way", ["x < best"], "x < best keeps the smallest item instead.")],
       "The condition is x > best. best always holds the largest value seen so far: whenever x is bigger it replaces "
       "best, so after the loop it is the largest item. Starting from the first item (not 0) also handles all-negative "
       "lists."),
    FB("algorithms", "intermediate", "general", "Missing code: the bubble sort step",
       """repeat n - 1 times:
    for j from 0 to n - 2:
        if a[j] > a[j + 1]:
            ____""",
       "Fill in the missing step of bubble sort.",
       ["swap a[j] and a[j + 1]", "swap a[j + 1] and a[j]", "swap(a[j], a[j + 1])", "swap(a[j], a[j+1])"],
       [("each pass bubbles the largest remaining value to the end; O(n^2)", ["bubble", "largest", "o(n^2)", "o(n²)"], 1)],
       [],
       "The missing step is swap a[j] and a[j + 1]. Neighbours that are out of order are swapped, so each pass "
       "bubbles the largest remaining value to the end of the list. That is about n² comparisons: O(n^2)."),
    FB("algorithms", "advanced", "general", "Missing code: the base case",
       """function power(b, e):      # e is a whole number >= 0
    if ____:
        return 1
    return b * power(b, e - 1)""",
       "Fill in the base case. What goes wrong without it?",
       ["e == 0", "e = 0", "e is 0", "e <= 0", "e < 1"],
       [("b to the power 0 is 1, and without a base case the recursion never stops (stack overflow)", ["never stops", "stack overflow", "infinite", "forever"], 1)],
       [],
       "The base case is e == 0, because b to the power 0 is 1. Each call lowers e by 1, so it eventually reaches 0 and "
       "stops; without a base case the recursion never stops and ends in a stack overflow."),
]
