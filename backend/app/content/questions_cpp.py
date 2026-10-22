"""Seed questions: C++ (C++17) — tracing, value semantics, pointers and references, RAII and smart pointers,
STL containers and algorithms, templates, undefined behaviour, complexity and design review."""

from app.content.qdef import Q

C = "cpp"

QUESTIONS_CPP = [
    # ── Beginner ────────────────────────────────────────────────────────────
    Q("code_tracing", "beginner", C, "Before or after the increment",
      """int i = 5;
int a = i++;
int b = ++i;
std::cout << a << " " << b << " " << i;""",
      "What is printed? Explain the difference between i++ and ++i.",
      [("prints 5 7 7", ["5 7 7"], 2),
       ("i++ returns the old value then increments (post-increment)", ["old value", "post-increment", "postfix", "then increment", "before increment"], 1),
       ("++i increments first and returns the new value (pre-increment)", ["new value", "pre-increment", "prefix", "increments first"], 1)],
      [("thinks a is 6", ["6 7 7"], "Post-increment yields the value before the increment, so a gets 5.")],
      "It prints 5 7 7. i++ is post-increment: it returns the old value (5) to a, then increments i to 6. ++i is "
      "pre-increment: it increments first (i becomes 7) and returns the new value, so b is 7, and i ends at 7."),
    Q("debugging", "beginner", C, "Loop that runs one step too far",
      """int sumAll(const std::vector<int>& v) {
    int total = 0;
    for (int i = 0; i <= v.size(); i++) {
        total += v[i];
    }
    return total;
}""",
      "The result is sometimes garbage and sometimes the program crashes. Find the bug and fix it.",
      [("i <= v.size() reads v[v.size()], one past the end", ["<=", "one past", "past the end", "out of bounds", "out-of-bounds", "off-by-one", "off by one"], 2),
       ("v[i] is not bounds-checked, so this is undefined behavior", ["undefined behavior", "undefined behaviour", "not checked", "no bounds check"], 1),
       ("fix: i < v.size(), or a range-for, or std::accumulate", ["i < v.size()", "range-for", "range for", "for (int x : v)", "accumulate"], 1)],
      [],
      "It is an off-by-one bug: i <= v.size() lets i reach v.size(), and v[v.size()] is one past the end. "
      "operator[] is not bounds-checked, so reading it is undefined behavior (garbage or a crash). Use i < v.size() "
      "(ideally with a size_t index), or a range-for for (int x : v) total += x;, or std::accumulate(v.begin(), "
      "v.end(), 0)."),
    Q("debugging", "beginner", C, "Adding a number to a string literal",
      """int score = 3;
std::string label = "Score: " + score;
std::cout << label;""",
      "It compiles but prints “re: ” instead of “Score: 3”. Why, and how do you fix it?",
      [("\"Score: \" is a const char* (char array), so + 3 is pointer arithmetic that skips 3 characters", ["pointer arithmetic", "const char*", "char*", "pointer", "char array"], 2),
       ("it does not convert the number to text", ["not convert", "doesn't convert", "no conversion", "not a std::string"], 1),
       ("fix: \"Score: \" + std::to_string(score), or std::string(\"Score: \") + ...", ["to_string", "std::string(", "ostringstream", "std::format"], 1)],
      [],
      "\"Score: \" is a string literal, a const char array that decays to a const char* pointer, not a std::string. So "
      "+ score is pointer arithmetic: it moves the pointer 3 characters forward, giving \"re: \"; it does not convert "
      "the number to text (and a big score would be undefined behavior). Fix it with \"Score: \" + "
      "std::to_string(score)."),
    Q("algorithmic_thinking", "beginner", C, "Checking every pair for duplicates",
      """bool hasDuplicate(const std::vector<int>& v) {
    for (size_t i = 0; i < v.size(); ++i)
        for (size_t j = i + 1; j < v.size(); ++j)
            if (v[i] == v[j]) return true;
    return false;
}""",
      "What is the time complexity? How could you make it faster?",
      [("O(n^2): every pair is compared", ["o(n^2)", "o(n²)", "o(n*n)", "quadratic", "n squared"], 2),
       ("use std::unordered_set for O(n) expected time", ["unordered_set", "hash set", "hash", "o(n)"], 1),
       ("or sort and compare neighbours in O(n log n)", ["sort", "n log n", "adjacent", "neighbour", "neighbor"], 1)],
      [],
      "It is O(n^2): the nested loops compare every pair, about n²/2 comparisons. Insert values into a "
      "std::unordered_set and stop when insert reports a duplicate, for O(n) expected time; or sort a copy and "
      "compare adjacent neighbours, O(n log n) with no hashing."),
    Q("edge_cases_testing", "beginner", C, "Average of an empty vector",
      """int average(const std::vector<int>& v) {
    int sum = 0;
    for (int x : v) sum += x;
    return sum / v.size();
}""",
      "Which inputs break this function or give a surprising answer? Name the tests you would write.",
      [("an empty vector divides by zero (undefined behavior / crash)", ["empty", "divide by zero", "division by zero", "zero"], 2),
       ("integer division truncates: {1, 2} gives 1, not 1.5", ["truncat", "integer division", "1.5", "decimal"], 1),
       ("negative values: sum is int but v.size() is unsigned, so the int is converted and the result is wrong", ["negative", "unsigned", "size_t"], 1)],
      [],
      "An empty vector makes v.size() zero, so it divides by zero: undefined behavior, typically a crash. Integer "
      "division truncates, so {1, 2} returns 1, not 1.5. Negative values are subtle: v.size() is unsigned (size_t), so "
      "a negative sum is converted to a huge unsigned number: {-6, 1, 2} returns 1431655764 instead of -1. Test empty, "
      "{1, 2}, {-6, 1, 2} and a large sum; cast the size to a signed type, return double and guard the empty case."),
    Q("code_review_design", "beginner", C, "Printing a list of names",
      """void printAll(std::vector<std::string> names) {
    for (int i = 0; i < names.size(); i++) {
        std::cout << names[i] << std::endl;
    }
}""",
      "Review this function. What would you change, and why?",
      [("names is passed by value, copying every string; take const std::vector<std::string>&", ["const&", "const &", "by value", "copy", "copies", "reference"], 2),
       ("use a range-for (no signed/unsigned index comparison)", ["range-for", "range for", "for (const auto&", "signed", "unsigned"], 1),
       ("std::endl flushes on every line; '\\n' is enough", ["endl", "flush", "\\n"], 1)],
      [],
      "names is passed by value, so every call copies the whole vector and every string; take const "
      "std::vector<std::string>& names instead (read-only reference, no copy). Use a range-for, for (const auto& n : "
      "names), which also avoids comparing a signed int with the unsigned size(). std::endl flushes the stream on "
      "every line; '\\n' is enough and faster."),
    Q("data_structures", "beginner", C, "Tracking unique visitors",
      """std::vector<std::string> seen;

void visit(const std::string& id) {
    if (std::find(seen.begin(), seen.end(), id) == seen.end()) {
        seen.push_back(id);
    }
}""",
      "With a million visits this gets slow. Why, and which container would you use?",
      [("std::find scans the whole vector: O(n) per visit, O(n^2) overall", ["o(n)", "linear", "scan", "o(n^2)", "o(n²)"], 2),
       ("use std::unordered_set: O(1) average insert/lookup and no duplicates", ["unordered_set"], 1),
       ("std::set if you need sorted order (O(log n))", ["std::set", "log n", "sorted"], 1)],
      [],
      "std::find scans the vector from the start, so each visit is O(n) and a million visits approach O(n^2). Use "
      "std::unordered_set<std::string>: seen.insert(id) is O(1) average and ignores duplicates automatically. Use "
      "std::set (O(log n)) if you also need the ids in sorted order."),
    Q("algorithms", "beginner", C, "Palindrome with two pointers",
      """bool isPalindrome(const std::string& s) {
    size_t i = 0, j = s.size();
    while (i + 1 < j) {
        if (s[i] != s[j - 1]) return false;
        ++i;
        --j;
    }
    return true;
}""",
      "Explain the approach, why it is correct (including for empty strings), and its cost.",
      [("two pointers move inward from both ends comparing characters", ["two pointer", "both ends", "inward", "from each end", "from the ends"], 2),
       ("O(n) time, O(1) extra space", ["o(n)", "linear"], 1),
       ("j is one past the right end so an empty string never underflows the unsigned index", ["empty", "underflow", "unsigned", "size_t", "one past"], 1)],
      [],
      "Two pointers start at both ends and move inward, comparing s[i] with s[j - 1]; any mismatch means it is not a "
      "palindrome, and if they meet every pair matched. It is O(n) time (n/2 comparisons) and O(1) extra space. j is "
      "kept one past the right end, so an empty string skips the loop and never underflows the unsigned size_t."),
    Q("algorithms", "beginner", C, "Largest value, safely",
      """int largest(const std::vector<int>& v) {
    int best = 0;
    for (int x : v)
        if (x > best) best = x;
    return best;
}""",
      "For which input is this wrong? Fix it, and say what the standard library offers.",
      [("all-negative input returns 0, which is not in the vector", ["negative", "all negative"], 2),
       ("start from v[0] (or INT_MIN) and decide what an empty vector means", ["v[0]", "int_min", "first element", "empty"], 1),
       ("std::max_element returns an iterator (end() for empty), O(n)", ["max_element"], 1)],
      [],
      "With all-negative input such as {-5, -2} it returns 0, which is not even in the vector. Start from the first "
      "element v[0] (and decide what an empty vector means: throw or return std::optional), or use "
      "std::max_element(v.begin(), v.end()), which returns an iterator, end() for empty input; both are O(n)."),

    # ── Intermediate ────────────────────────────────────────────────────────
    Q("code_tracing", "intermediate", C, "A function that remembers",
      """int nextId() {
    static int n = 0;
    return ++n;
}

int main() {
    nextId();
    std::cout << nextId() << nextId() << " " << nextId();
}""",
      "What is printed (C++17)? Explain what static does to a local variable.",
      [("prints 23 4", ["23 4"], 2),
       ("static: n is initialised once and keeps its value between calls", ["once", "keeps its value", "between calls", "persist", "lifetime"], 1),
       ("since C++17 the operands of << are evaluated left to right", ["left to right", "c++17", "sequenced", "order"], 1)],
      [("thinks n resets to 0 on every call", ["1 1", "11 1", "resets"], "A static local is created once; it is not reinitialised on later calls.")],
      "It prints 23 4. A static local variable is initialised only once and keeps its value between calls (it "
      "lives for the whole program). The first call returns 1 (discarded), then 2, 3 and 4. Since C++17 the operands "
      "of a << chain are sequenced left to right, so they appear in that order."),
    Q("code_tracing", "intermediate", C, "Counting shared owners",
      """#include <iostream>
#include <memory>

int main() {
    auto p = std::make_shared<int>(42);
    {
        auto q = p;
        std::cout << p.use_count() << " ";
    }
    std::cout << p.use_count() << " " << *p;
}""",
      "What is printed? When is the int finally deleted?",
      [("prints 2 1 42", ["2 1 42"], 2),
       ("copying a shared_ptr increases the reference count; q's destruction at } lowers it", ["reference count", "use_count", "count", "copy"], 1),
       ("the int is deleted when the last owner (p) is destroyed, at the end of main", ["last owner", "last shared_ptr", "reaches 0", "reaches zero", "end of main"], 1)],
      [],
      "It prints 2 1 42. Copying a shared_ptr (auto q = p) shares ownership and raises the reference count (use_count) "
      "to 2. At the closing } q is destroyed and the count drops to 1. The int is deleted only when the last owner, p, "
      "is destroyed at the end of main and the count reaches 0."),
    Q("debugging", "intermediate", C, "Returning a reference to a local",
      """const std::string& greeting(const std::string& name) {
    std::string text = "Hello, " + name;
    return text;
}

int main() {
    std::cout << greeting("Ada");
}""",
      "This sometimes prints garbage or crashes. What is the root cause and the fix?",
      [("returns a reference to a local that is destroyed when the function returns (dangling reference)", ["dangling", "destroyed", "local", "goes out of scope", "out of scope"], 2),
       ("using it is undefined behavior", ["undefined behavior", "undefined behaviour"], 1),
       ("fix: return std::string by value (move/copy elision makes it cheap)", ["by value", "return std::string", "elision", "move", "rvo"], 1)],
      [],
      "greeting returns a reference to text, a local that is destroyed when the function returns, so the caller holds "
      "a dangling reference. Reading it is undefined behavior (garbage, a crash, or it seems to work). Return "
      "std::string by value: copy elision / move semantics (RVO) make that cheap."),
    Q("debugging", "intermediate", C, "Deleting through the base class",
      """struct Shape {
    ~Shape() { std::cout << "~Shape "; }
};
struct Image : Shape {
    std::vector<char> pixels = std::vector<char>(1'000'000);
    ~Image() { std::cout << "~Image "; }
};

int main() {
    Shape* s = new Image();
    delete s;   // prints only "~Shape "
}""",
      "Why is ~Image never called, what goes wrong, and how do you fix it?",
      [("the base destructor is not virtual, so delete through Shape* does not call ~Image", ["virtual destructor", "not virtual", "virtual ~shape", "virtual"], 2),
       ("this is undefined behavior and leaks the pixel memory", ["undefined behavior", "undefined behaviour", "leak"], 1),
       ("fix: virtual ~Shape() = default; and prefer std::unique_ptr<Shape> over new/delete", ["virtual ~shape()", "unique_ptr", "make_unique"], 1)],
      [],
      "Shape's destructor is not virtual, so delete s through a Shape* calls only ~Shape and never ~Image. That is "
      "undefined behavior, and in practice the vector inside Image is never destroyed, a leak. Declare virtual "
      "~Shape() = default; in any base class used polymorphically, and own the object with "
      "std::unique_ptr<Shape> (std::make_unique<Image>()) instead of raw new/delete."),
    Q("algorithmic_thinking", "intermediate", C, "Copying the vector on every query",
      """bool contains(std::vector<int> v, int x) {
    for (int y : v) if (y == x) return true;
    return false;
}

int countHits(const std::vector<int>& data, const std::vector<int>& queries) {
    int hits = 0;
    for (int q : queries) if (contains(data, q)) ++hits;
    return hits;
}""",
      "data has n items and queries has m. What does countHits cost, and how would you speed it up?",
      [("O(n·m): each query copies the n-element vector and scans it", ["o(n*m)", "o(nm)", "o(n·m)", "o(m*n)", "o(mn)", "o(m·n)", "n times m", "m times n"], 2),
       ("pass by const reference to stop the O(n) copy (and allocation) per call", ["const&", "const &", "reference", "copy", "copies"], 1),
       ("build an unordered_set once: O(n + m) expected (or sort + binary_search)", ["unordered_set", "o(n + m)", "o(n+m)", "binary_search", "hash"], 1)],
      [],
      "It is O(n·m): for each of the m queries, contains copies all n elements (v is taken by value, which also "
      "allocates) and then scans them. Passing const std::vector<int>& removes the copy but the scan is still O(n). "
      "Build a std::unordered_set<int> from data once and look each query up: O(n + m) expected; or sort once and use "
      "std::binary_search, O((n + m) log n)."),
    Q("algorithmic_thinking", "intermediate", C, "Building a string piece by piece",
      """std::string joinA(const std::vector<std::string>& parts) {
    std::string out;
    for (const auto& p : parts) out = out + p + ",";
    return out;
}

std::string joinB(const std::vector<std::string>& parts) {
    std::string out;
    for (const auto& p : parts) { out += p; out += ','; }
    return out;
}""",
      "Compare the cost of joinA and joinB for a large number of parts.",
      [("joinA is O(n^2) in total length: out + p builds a new string copying everything so far", ["o(n^2)", "o(n²)", "quadratic", "new string", "copies everything", "temporary"], 2),
       ("joinB appends in place: amortized O(n) total", ["amortized", "amortised", "in place", "o(n)", "linear"], 1),
       ("can reserve() the final size to avoid reallocations", ["reserve"], 1)],
      [],
      "joinA writes out = out + p + \",\", which builds a new temporary string and copies everything accumulated so "
      "far on every iteration, so the total cost is O(n^2) in the output length. joinB appends in place with +=, "
      "which grows the buffer geometrically: amortized O(n) total. Calling out.reserve(total) first removes even the "
      "reallocations."),
    Q("edge_cases_testing", "intermediate", C, "Midpoint of two indexes",
      """int binarySearch(const std::vector<int>& v, int target) {
    int lo = 0, hi = static_cast<int>(v.size()) - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (v[mid] == target) return mid;
        if (v[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}""",
      "This works in tests but fails on huge inputs. Which edge case breaks it, and what else would you test?",
      [("lo + hi can overflow int for very large indexes (signed overflow is undefined behavior)", ["overflow", "lo + hi", "undefined behavior", "undefined behaviour"], 2),
       ("fix: mid = lo + (hi - lo) / 2 or std::midpoint", ["lo + (hi - lo) / 2", "lo + (hi-lo)/2", "std::midpoint", "midpoint"], 1),
       ("also test empty vector, single element, target at both ends, missing target and duplicates", ["empty", "single element", "one element", "duplicate", "first", "last", "missing"], 1)],
      [],
      "For very large vectors (indexes near INT_MAX) lo + hi can overflow int, and signed overflow is undefined "
      "behavior, so mid can become negative. Use mid = lo + (hi - lo) / 2 or std::midpoint(lo, hi) (or just "
      "std::lower_bound). Also test an empty vector, a single element, the target at the first and last position, a "
      "missing target and duplicates."),
    Q("edge_cases_testing", "intermediate", C, "Parsing numbers with stoi",
      """int parseQuantity(const std::string& text) {
    return std::stoi(text);
}
// parseQuantity("12")    -> 12
// parseQuantity("12abc") -> ?
// parseQuantity("abc")   -> ?
// parseQuantity("99999999999") -> ?""",
      "What happens for each commented input, and how would you make parsing strict?",
      [("\"12abc\" quietly returns 12 (stoi stops at the first non-digit)", ["returns 12", "stops at", "partial", "ignores the rest", "trailing"], 2),
       ("\"abc\" throws std::invalid_argument; the huge value throws std::out_of_range", ["invalid_argument", "out_of_range"], 1),
       ("strict: check the pos out-parameter equals text.size(), or use std::from_chars, and catch exceptions", ["pos", "from_chars", "catch", "try"], 1)],
      [],
      "\"12abc\" quietly returns 12, because stoi stops at the first non-digit and ignores the rest. \"abc\" has no "
      "digits, so it throws std::invalid_argument, and 99999999999 does not fit in an int, so it throws "
      "std::out_of_range. For strict parsing pass a size_t pos out-parameter and check pos == text.size(), or use "
      "std::from_chars, and catch (or report) the errors."),
    Q("code_review_design", "intermediate", C, "A class that owns raw memory",
      """class Buffer {
public:
    explicit Buffer(size_t n) : size_(n), data_(new int[n]) {}
    ~Buffer() { delete[] data_; }
    int& operator[](size_t i) { return data_[i]; }
private:
    size_t size_;
    int* data_;
};

void process() {
    Buffer a(10);
    Buffer b = a;   // ?
}""",
      "What goes wrong in process(), and how would you redesign Buffer?",
      [("the default copy copies the pointer, so a and b both delete[] the same memory (double free)", ["double free", "double delete", "same memory", "same pointer", "shallow copy"], 2),
       ("violates the rule of three/five: a destructor without copy constructor/assignment", ["rule of three", "rule of five", "copy constructor", "copy assignment"], 1),
       ("best fix: hold a std::vector<int> (rule of zero), or define/delete the copy operations", ["std::vector", "rule of zero", "= delete", "unique_ptr"], 1)],
      [],
      "The compiler-generated copy constructor makes a shallow copy of the pointer, so a and b point to the same "
      "memory and both destructors run delete[] on it: a double free, which is undefined behavior. Buffer breaks the "
      "rule of three/five (it has a destructor but no copy constructor or copy assignment). Best: store a "
      "std::vector<int> and write no special members at all (rule of zero); otherwise implement deep copies and moves, "
      "or = delete copying and hold a std::unique_ptr<int[]>."),
    Q("code_review_design", "intermediate", C, "A squaring macro",
      """#define SQUARE(x) x * x

int a = SQUARE(1 + 2);   // expected 9
int i = 3;
int b = SQUARE(i++);""",
      "What is a, what is wrong with b, and what should replace the macro?",
      [("a is 5: the macro pastes text, giving 1 + 2 * 1 + 2", ["is 5", "a = 5", "1 + 2 * 1 + 2", "text substitution", "pastes"], 2),
       ("SQUARE(i++) becomes i++ * i++: two unsequenced modifications, undefined behavior", ["i++ * i++", "undefined behavior", "undefined behaviour", "twice", "unsequenced"], 1),
       ("use a constexpr (or inline/template) function instead", ["constexpr", "inline function", "template", "function"], 1)],
      [],
      "a is 5, not 9: a macro is plain text substitution, so SQUARE(1 + 2) becomes 1 + 2 * 1 + 2. SQUARE(i++) becomes "
      "i++ * i++, which modifies i twice without sequencing: undefined behavior. Replace it with a function, e.g. "
      "constexpr int square(int x) { return x * x; } (or a template), which evaluates its argument once, is "
      "type-checked and still runs at compile time when possible."),
    Q("data_structures", "intermediate", C, "Ordered or unordered map",
      """std::map<std::string, int> ordered = {{"pear", 3}, {"apple", 5}, {"fig", 1}};
std::unordered_map<std::string, int> hashed(ordered.begin(), ordered.end());

for (const auto& [k, v] : ordered) std::cout << k << " ";
// for (const auto& [k, v] : hashed) ... prints in what order?""",
      "What does the first loop print? Compare std::map and std::unordered_map and say when you'd pick each.",
      [("prints apple fig pear (map is sorted by key)", ["apple fig pear"], 2),
       ("map is a balanced tree: O(log n) operations, ordered iteration", ["o(log n)", "log n", "tree", "red-black"], 1),
       ("unordered_map is a hash table: O(1) average, iteration order unspecified", ["hash", "o(1)", "unspecified", "no order", "not sorted", "any order"], 1)],
      [],
      "It prints apple fig pear: std::map keeps keys sorted. map is a balanced binary tree (red-black), so lookups and "
      "inserts are O(log n) and iteration is ordered — pick it for sorted output or range queries (lower_bound). "
      "unordered_map is a hash table: O(1) average lookups, but iteration order is unspecified — pick it for fast "
      "lookups when order doesn't matter."),
    Q("algorithms", "intermediate", C, "Removing duplicates with sort and unique",
      """std::vector<int> v = {3, 1, 3, 2, 1};
std::sort(v.begin(), v.end());
v.erase(std::unique(v.begin(), v.end()), v.end());
for (int x : v) std::cout << x << " ";""",
      "What is printed? Explain why both sort and erase are needed, and the cost.",
      [("prints 1 2 3", ["1 2 3"], 2),
       ("unique only removes adjacent duplicates, so the range must be sorted first", ["adjacent", "consecutive", "next to each other", "sorted first"], 1),
       ("unique doesn't shrink the vector: it returns the new logical end, and erase removes the tail", ["new end", "logical end", "does not shrink", "doesn't shrink", "tail", "erase"], 1),
       ("O(n log n) for the sort; unique and erase are O(n)", ["n log n"], 1)],
      [],
      "It prints 1 2 3. std::unique only collapses adjacent (consecutive) duplicates, so the vector is sorted first to "
      "bring equal values next to each other. unique doesn't shrink the vector: it moves the kept values forward and "
      "returns the new logical end, and erase removes the leftover tail. The cost is O(n log n) for the sort; unique "
      "and erase are O(n)."),
    Q("algorithms", "intermediate", C, "Finding a value with lower_bound",
      """std::vector<int> v = {2, 4, 4, 8, 10};
auto it = std::lower_bound(v.begin(), v.end(), 5);
std::cout << (it - v.begin()) << " " << *it;""",
      "What is printed? Explain what lower_bound returns, its requirement and its cost.",
      [("prints 3 8", ["3 8"], 2),
       ("lower_bound returns the first element not less than the value (>= 5)", ["first element", "not less than", ">= 5", "greater than or equal"], 1),
       ("requires a sorted range; binary search, O(log n)", ["sorted", "binary search", "o(log n)", "log n"], 1)],
      [],
      "It prints 3 8. std::lower_bound returns an iterator to the first element not less than 5, i.e. the first "
      "element >= 5, which is 8 at index 3. It requires a sorted range and uses binary search, O(log n) comparisons. "
      "If every element were smaller it would return end(), which must not be dereferenced."),

    # ── Advanced ───────────────────────────────────────────────────────────
    Q("code_tracing", "advanced", C, "Passing a derived object by value",
      """struct Animal {
    virtual std::string sound() const { return "..."; }
    virtual ~Animal() = default;
};
struct Dog : Animal {
    std::string sound() const override { return "Woof"; }
};

void byValue(Animal a)      { std::cout << a.sound() << " "; }
void byRef(const Animal& a) { std::cout << a.sound(); }

int main() {
    Dog d;
    byValue(d);
    byRef(d);
}""",
      "What is printed? Explain why the two calls differ.",
      [("prints ... Woof", ["... woof"], 2),
       ("passing by value slices the Dog into a plain Animal (object slicing)", ["slic"], 1),
       ("through a reference the virtual call dispatches to Dog::sound (dynamic dispatch)", ["virtual", "dynamic dispatch", "vtable", "override"], 1)],
      [("thinks both print Woof", ["woof woof"], "byValue copies only the Animal part of d, so the object really is an Animal and calls Animal::sound.")],
      "It prints ... Woof. byValue(Animal a) copies only the Animal part of the Dog, so the object is sliced into a "
      "plain Animal (object slicing) and Animal::sound runs. byRef takes a reference to the real Dog, so the virtual "
      "call is dynamically dispatched (via the vtable) to the override Dog::sound. Take polymorphic objects by "
      "reference or pointer."),
    Q("code_tracing", "advanced", C, "Constructors, destructors and scope",
      """struct Noisy {
    char id;
    Noisy(char c) : id(c) { std::cout << "+" << id; }
    ~Noisy() { std::cout << "-" << id; }
};

int main() {
    Noisy a('a');
    {
        Noisy b('b');
    }
    Noisy c('c');
}""",
      "What is printed? State the rule that decides when each destructor runs.",
      [("prints +a+b-b+c-c-a", ["+a+b-b+c-c-a"], 2),
       ("b is destroyed at the end of its inner block", ["end of its block", "end of the block", "inner block", "closing brace", "goes out of scope", "leaves scope"], 1),
       ("locals are destroyed in reverse order of construction (this is what RAII relies on)", ["reverse order", "reverse", "lifo", "raii"], 1)],
      [],
      "It prints +a+b-b+c-c-a. Each object's destructor runs automatically when it goes out of scope: b is destroyed "
      "at the closing brace of its inner block, before c is built. At the end of main the remaining locals are "
      "destroyed in reverse order of construction, c then a. RAII relies on exactly this rule to release resources."),
    Q("code_tracing", "advanced", C, "Moving a unique_ptr",
      """#include <iostream>
#include <memory>

int main() {
    auto a = std::make_unique<int>(5);
    auto b = std::move(a);
    std::cout << (a ? "a " : "null ") << *b;
    // auto c = b;   // what if we uncomment this?
}""",
      "What is printed? What happens if the commented line is uncommented?",
      [("prints null 5", ["null 5"], 2),
       ("std::move transfers ownership: a becomes empty (nullptr) and b owns the int", ["transfer", "ownership", "a is empty", "a becomes null", "nullptr"], 1),
       ("unique_ptr cannot be copied, so auto c = b is a compile error", ["cannot be copied", "can't be copied", "not copyable", "copy constructor is deleted", "deleted", "compile error"], 1)],
      [],
      "It prints null 5. std::move(a) lets b's move constructor transfer ownership of the int: a is left empty "
      "(nullptr, so it tests false) and b now owns it. unique_ptr models sole ownership, so it cannot be copied: its "
      "copy constructor is deleted and auto c = b is a compile error (auto c = std::move(b) would work)."),
    Q("debugging", "advanced", C, "Erasing while iterating",
      """void removeEvens(std::vector<int>& v) {
    for (auto it = v.begin(); it != v.end(); ++it) {
        if (*it % 2 == 0) {
            v.erase(it);
        }
    }
}""",
      "This crashes or skips elements. Explain the root cause and give two correct versions.",
      [("erase invalidates it (and later iterators), so ++it on it is undefined behavior", ["invalidat", "undefined behavior", "undefined behaviour"], 2),
       ("fix: it = v.erase(it) and only ++it when nothing was erased", ["it = v.erase(it)", "returns the next", "returns an iterator"], 1),
       ("or erase-remove idiom / std::erase_if (C++20), which is also O(n)", ["remove_if", "erase-remove", "erase_if"], 1)],
      [],
      "v.erase(it) invalidates it and every iterator after it, so the following ++it uses an invalid iterator: "
      "undefined behavior (crashes, skipped elements, running past end). Fix 1: it = v.erase(it), which returns the "
      "next valid iterator, and only ++it when nothing was erased. Fix 2: the erase-remove idiom, "
      "v.erase(std::remove_if(v.begin(), v.end(), isEven), v.end()), or std::erase_if(v, isEven) in C++20, which is "
      "O(n) instead of O(n^2)."),
    Q("algorithmic_thinking", "advanced", C, "Inserting at the front of a vector",
      """std::vector<int> reversedCopy(const std::vector<int>& in) {
    std::vector<int> out;
    for (int x : in) {
        out.insert(out.begin(), x);
    }
    return out;
}""",
      "What is the time complexity, and what are better options?",
      [("O(n^2): each front insert shifts every existing element", ["o(n^2)", "o(n²)", "quadratic", "shift"], 2),
       ("vector is contiguous, so only the back is cheap (amortized O(1) push_back)", ["contiguous", "push_back", "amortized", "amortised"], 1),
       ("use reverse iterators / std::reverse (O(n)) or std::deque push_front", ["rbegin", "reverse", "deque", "push_front"], 1)],
      [],
      "It is O(n^2): a vector is contiguous, so each insert at begin() shifts every existing element one place right. "
      "Only the back is cheap: push_back is amortized O(1). Build it in O(n) with std::vector<int> out(in.rbegin(), "
      "in.rend()), or push_back then std::reverse; if you truly need cheap insertion at the front, std::deque has O(1) "
      "push_front."),
    Q("edge_cases_testing", "advanced", C, "Counting down with size_t",
      """void printBackwards(const std::vector<int>& v) {
    for (size_t i = v.size() - 1; i >= 0; --i) {
        std::cout << v[i] << " ";
    }
}""",
      "Which inputs break this loop, and how do you write it correctly?",
      [("size_t is unsigned, so i >= 0 is always true: the loop never ends normally", ["unsigned", "always true", "never negative", "never ends", "infinite"], 2),
       ("decrementing 0 wraps to a huge value, reading out of bounds; an empty vector starts at that huge value", ["wrap", "huge", "out of bounds", "empty"], 1),
       ("fix: for (size_t i = v.size(); i-- > 0;) or reverse iterators (rbegin/rend)", ["i-- > 0", "rbegin", "reverse iterator", "std::views::reverse"], 1)],
      [],
      "size_t is unsigned, so i >= 0 is always true: the loop never ends normally. After printing v[0], --i wraps "
      "around to a huge value and v[i] reads far out of bounds (undefined behavior); an empty vector is even worse, "
      "because v.size() - 1 already wraps to the huge value. Write for (size_t i = v.size(); i-- > 0;) or use reverse "
      "iterators: for (auto it = v.rbegin(); it != v.rend(); ++it). Test empty, one element and several elements."),
    Q("code_review_design", "advanced", C, "A generic max function",
      """template <typename T>
T maxOf(T a, T b) {
    return a > b ? a : b;
}

auto x = maxOf(3, 4.5);           // ?
auto y = maxOf("pear", "apple");  // ?""",
      "Review this template. What happens on each line, and how would you improve it?",
      [("maxOf(3, 4.5) fails to compile: T is deduced as both int and double (template argument deduction conflict)", ["deduc", "int and double", "conflict", "compile error", "ambiguous"], 2),
       ("string literals deduce T = const char*, so it compares pointer addresses, not text", ["const char*", "pointer", "address"], 1),
       ("fix: maxOf<double>(3, 4.5) or std::max, std::string / std::string_view arguments, and take const T&", ["maxof<double>", "std::max", "std::string", "string_view", "const t&"], 1)],
      [],
      "maxOf(3, 4.5) does not compile: template argument deduction sees T as int from 3 and double from 4.5, a "
      "conflict. With string literals T is deduced as const char*, so a > b compares pointer addresses, not text, "
      "and the result is meaningless. Call maxOf<double>(3, 4.5) (or use std::max), pass std::string or "
      "std::string_view to compare text, and take const T& to avoid copying large types (or constrain T with a "
      "concept in C++20)."),
    Q("code_review_design", "advanced", C, "Leaking on the early return",
      """bool loadConfig(const char* path) {
    FILE* f = std::fopen(path, "r");
    char* buf = new char[4096];
    if (!f) return false;
    if (std::fread(buf, 1, 4096, f) == 0) return false;
    parse(buf);
    delete[] buf;
    std::fclose(f);
    return true;
}""",
      "Review the resource handling. What leaks, and how does RAII fix it?",
      [("early returns (and exceptions from parse) skip delete[] / fclose, leaking memory and the file handle", ["leak", "early return", "skip", "exception"], 2),
       ("RAII: tie each resource to an object whose destructor releases it", ["raii", "destructor"], 1),
       ("use std::vector<char> / std::string and std::ifstream (or unique_ptr with a deleter)", ["std::vector", "ifstream", "unique_ptr", "fstream"], 1)],
      [],
      "Every early return leaks: if fopen fails, buf is never freed; if fread reads nothing, both buf and the FILE* "
      "leak; and if parse throws an exception, delete[] and fclose are skipped too. RAII fixes this by tying each "
      "resource to an object whose destructor releases it on every path: use std::vector<char> buf(4096) (or "
      "std::string) and std::ifstream, or a std::unique_ptr<FILE, decltype(&std::fclose)>, and drop the manual "
      "cleanup."),
    Q("data_structures", "advanced", C, "Top of the priority queue",
      """std::priority_queue<int> pq;
for (int x : {5, 1, 8, 3}) pq.push(x);
while (!pq.empty()) {
    std::cout << pq.top() << " ";
    pq.pop();
}""",
      "What is printed? How would you get the smallest value first, and what does each operation cost?",
      [("prints 8 5 3 1 (a max-heap by default)", ["8 5 3 1"], 2),
       ("min-heap: std::priority_queue<int, std::vector<int>, std::greater<int>>", ["greater"], 1),
       ("push/pop are O(log n), top is O(1)", ["o(log n)", "log n"], 1)],
      [],
      "It prints 8 5 3 1: std::priority_queue is a binary max-heap by default, so top() is always the largest. For "
      "smallest-first use std::priority_queue<int, std::vector<int>, std::greater<int>>. push and pop are O(log n) "
      "and top is O(1)."),
    Q("algorithms", "advanced", C, "Climbing stairs with memoization",
      """long long ways(int n, std::vector<long long>& memo) {
    if (n <= 1) return 1;
    if (memo[n] != 0) return memo[n];
    return memo[n] = ways(n - 1, memo) + ways(n - 2, memo);
}

int main() {
    std::vector<long long> memo(51, 0);
    std::cout << ways(5, memo);   // steps of 1 or 2
}""",
      "What is printed? Explain the recurrence, why memoization matters and the complexity.",
      [("prints 8", ["prints 8", "output is 8", "it prints 8", "8 ways", "answer is 8"], 2),
       ("ways(n) = ways(n-1) + ways(n-2): the last step was 1 or 2 stairs", ["ways(n - 1) + ways(n - 2)", "ways(n-1) + ways(n-2)", "last step", "fibonacci"], 1),
       ("memo makes it O(n) time instead of exponential O(2^n); O(n) space", ["o(n)", "exponential", "o(2^n)"], 1),
       ("long long because the counts grow fast (Fibonacci)", ["long long", "overflow", "grow"], 1)],
      [],
      "It prints 8. The last move was either 1 stair or 2, so ways(n) = ways(n-1) + ways(n-2) with ways(0) = ways(1) "
      "= 1: the Fibonacci sequence 1, 1, 2, 3, 5, 8. Without the memo the same subproblems are recomputed and the "
      "time is exponential, about O(2^n); storing each result once makes it O(n) time and O(n) space. long long is "
      "used because the counts grow fast and an int would overflow from n = 46."),
    Q("algorithms", "advanced", C, "Shortest path in an unweighted graph",
      """std::vector<int> bfs(const std::vector<std::vector<int>>& adj, int start) {
    std::vector<int> dist(adj.size(), -1);
    std::queue<int> q;
    dist[start] = 0;
    q.push(start);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u])
            if (dist[v] == -1) { dist[v] = dist[u] + 1; q.push(v); }
    }
    return dist;
}""",
      "Why does this compute shortest distances, and what does it cost? What does -1 mean in the result?",
      [("BFS visits nodes in order of distance (a FIFO queue processes layer by layer), so the first time a node is reached is via a shortest path", ["layer", "level", "fifo", "in order of distance", "first time"], 2),
       ("O(V + E) time: each vertex is queued once and each edge checked once", ["o(v + e)", "o(v+e)", "o(n + m)", "o(n+m)"], 1),
       ("-1 marks unreachable nodes; only valid for unweighted edges (weighted needs Dijkstra)", ["unreachable", "not reachable", "dijkstra", "unweighted"], 1)],
      [],
      "BFS uses a FIFO queue, so it processes nodes layer by layer in order of distance: all nodes at distance d "
      "before any at d + 1. Therefore the first time a node is reached is via a shortest path, and dist[v] == -1 "
      "stops it being updated again. It is O(V + E): each vertex is queued once and each edge checked once. -1 in the "
      "result marks unreachable nodes. This only works for unweighted edges; with weights use Dijkstra."),
]
