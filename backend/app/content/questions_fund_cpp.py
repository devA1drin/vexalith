"""Fundamentals: C++ — first steps for complete beginners (C++17)."""

from app.content.qdef import Q

F, C = "fundamentals", "cpp"

QUESTIONS_FUND_CPP = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", C, "Your first cout",
      """#include <iostream>

int main() {
    std::cout << "Hello" << ", " << "C++!" << '\\n';
    std::cout << 2 + 3 << '\\n';
    return 0;
}""",
      "What exactly is printed? Explain what #include, std::cout and << do.",
      [("prints Hello, C++! then 5 on the next line", ["hello, c++!", "hello, c++"], 2),
       ("<< sends each value to cout (the screen) in order, left to right", ["<<", "send", "insert", "in order", "left to right"], 1),
       ("#include <iostream> brings in cout; std:: is the standard namespace", ["iostream", "std::", "namespace", "standard library"], 1),
       ("'\\n' starts a new line; 2 + 3 is computed first, so it prints 5", ["new line", "newline", "\\n", "line break"], 1)],
      [("thinks it prints the text 2 + 3", ["prints 2 + 3", "prints \"2 + 3\"", "the text 2 + 3"], "2 + 3 is not in quotes, so it is an expression: C++ computes 5 and prints the number.")],
      "It prints Hello, C++! on the first line and 5 on the second. #include <iostream> brings in the input/output "
      "library, and std:: means cout comes from the standard namespace. Each << sends the next value to cout (the "
      "screen) in order, left to right. '\\n' starts a new line. 2 + 3 is not in quotes, so it is computed first and "
      "the number 5 is printed."),
    Q(F, "beginner", C, "The missing semicolon",
      """#include <iostream>

int main() {
    int score = 10
    std::cout << score << '\\n';
}""",
      "This program does not compile. What is wrong, and how do you fix it?",
      [("compile error: the line int score = 10 is missing a semicolon", ["semicolon", ";", "compile error", "compiler error", "syntax error"], 2),
       ("every statement in C++ ends with ;", ["every statement", "statement", "end of", "ends with"], 1)],
      [],
      "It is a compile error: the statement int score = 10 is missing its semicolon. In C++ every statement ends "
      "with ;, so the compiler reads on into the next line and gets confused. Write int score = 10; and the program "
      "prints 10."),
    Q(F, "beginner", C, "Whole-number division",
      """#include <iostream>

int main() {
    std::cout << 7 / 2 << " " << 7 % 2 << " " << 7.0 / 2 << '\\n';
}""",
      "What is printed? Explain why the first and the last results differ.",
      [("prints 3 1 3.5", ["3 1 3.5"], 2),
       ("int / int is integer division: the decimal part is thrown away", ["integer division", "whole number", "truncat", "thrown away", "drops", "discard"], 1),
       ("% gives the remainder; 7.0 is a double, so the division keeps the decimals", ["remainder", "double", "decimal", "floating"], 1)],
      [("thinks 7 / 2 rounds to 4", ["rounds to 4", "rounds up", "prints 4"], "Integer division never rounds: it simply drops the fractional part, so 7 / 2 is 3.")],
      "It prints 3 1 3.5. When both sides are int, / is integer division: the decimal part is thrown away, so 7 / 2 "
      "is 3 (it does not round). % gives the remainder, 1. 7.0 is a double, so 7.0 / 2 keeps the decimals and gives "
      "3.5."),
    Q(F, "beginner", C, "Choosing a grade",
      """int score = 72;
if (score >= 90) {
    std::cout << "A";
} else if (score >= 70) {
    std::cout << "B";
} else {
    std::cout << "C";
}""",
      "What is printed, and how does C++ choose which branch runs?",
      [("prints B", ["prints b", "output is b", "b is printed", "it prints b", "answer is b", "\"b\""], 2),
       ("conditions are checked top to bottom and only the first true branch runs", ["top to bottom", "first true", "in order", "only one", "first condition"], 1)],
      [],
      "It prints B. C++ checks the conditions from top to bottom: 72 >= 90 is false, 72 >= 70 is true, so only that "
      "first true branch runs and the else is skipped."),
    Q(F, "beginner", C, "Counting with a for loop",
      """for (int i = 0; i < 3; i++) {
    std::cout << i << " ";
}
std::cout << "done";""",
      "What is printed? Describe the three parts inside the for (...).",
      [("prints 0 1 2 done", ["0 1 2 done", "0 1 2"], 2),
       ("start at 0, keep going while i < 3, add 1 after each pass", ["start", "while", "i++", "add 1", "increase", "each pass", "each time"], 1),
       ("stops when i becomes 3 because 3 < 3 is false", ["3 < 3", "becomes 3", "reaches 3", "is false", "stops"], 1)],
      [("thinks the loop prints 3", ["0 1 2 3", "1 2 3"], "The condition i < 3 is checked before each pass, so when i is 3 the loop stops before printing it.")],
      "It prints 0 1 2 done. The for has three parts: int i = 0 runs once at the start, i < 3 is checked before every "
      "pass, and i++ adds 1 after each pass. When i becomes 3, 3 < 3 is false, so the loop stops and then done is "
      "printed."),
    Q(F, "beginner", C, "A decimal in an int",
      """int price = 9.99;
double exact = 9.99;
std::cout << price << " " << exact;""",
      "What is printed, and why are the two numbers different?",
      [("prints 9 9.99", ["9 9.99"], 2),
       ("an int can only hold whole numbers, so the decimal part is cut off (truncated, not rounded)", ["whole number", "truncat", "cut off", "dropped", "not rounded", "decimal part"], 1),
       ("double stores decimal (floating-point) numbers", ["double", "floating", "decimal number"], 1)],
      [("thinks the int rounds to 10", ["rounds to 10", "prints 10"], "Converting a double to int truncates toward zero: 9.99 becomes 9, not 10.")],
      "It prints 9 9.99. An int can only hold whole numbers, so 9.99 is converted and the decimal part is cut off "
      "(truncated, not rounded) to 9. A double stores decimal (floating-point) numbers, so exact keeps 9.99. Many "
      "compilers warn about this narrowing conversion."),
    Q(F, "beginner", C, "Reading a number with cin",
      """#include <iostream>

int main() {
    int age;
    std::cout << "Age? ";
    std::cin >> age;
    std::cout << "Next year: " << age + 1 << '\\n';
}""",
      "The user types 20 and presses Enter. What is printed, and what does >> do here?",
      [("prints Age? then Next year: 21", ["next year: 21", "21"], 2),
       ("cin >> age reads what the user types and stores it in age as an int", ["reads", "stores", "input", "keyboard", "types"], 1),
       (">> is the opposite direction of <<: data flows from cin into the variable", ["opposite", "into the variable", "into age", "from cin"], 1)],
      [],
      "It prints Age? and, after the user types 20, Next year: 21. std::cin >> age reads what the user types and "
      "stores it in age as an int. >> points the other way from <<: data flows from cin into the variable. Then age + "
      "1 is 21."),
    Q(F, "beginner", C, "One equals sign too few",
      """int x = 5;
if (x = 0) {
    std::cout << "zero";
} else {
    std::cout << "not zero";
}
std::cout << " " << x;""",
      "What is printed? Explain the bug and the fix.",
      [("prints not zero 0", ["not zero 0"], 2),
       ("x = 0 assigns 0 (it does not compare), and 0 counts as false", ["assign", "not compar", "counts as false", "is false", "falsy"], 1),
       ("fix: use == to compare", ["=="], 1)],
      [("thinks it prints zero", ["prints zero", "output is zero"], "x = 0 stores 0 in x; the value of the assignment is 0, which counts as false, so the else runs.")],
      "It prints not zero 0. x = 0 is an assignment, not a comparison: it stores 0 in x, and the value 0 counts as "
      "false, so the else branch runs, and x is now 0. To compare, use x == 0. Turning on compiler warnings (-Wall) "
      "flags this mistake."),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", C, "Copy or reference parameter",
      """void addOne(int n) { n++; }
void addOneRef(int& n) { n++; }

int main() {
    int a = 5, b = 5;
    addOne(a);
    addOneRef(b);
    std::cout << a << " " << b;
}""",
      "What is printed? Explain the difference the & makes.",
      [("prints 5 6", ["5 6"], 2),
       ("without & the function gets a copy, so a is unchanged", ["copy", "by value", "unchanged"], 1),
       ("int& is a reference: n is another name for b, so b changes", ["reference", "another name", "alias", "same variable", "by reference"], 1)],
      [("thinks both change", ["6 6"], "addOne receives a copy of a, so incrementing the copy does not touch a.")],
      "It prints 5 6. addOne(int n) receives a copy of a (pass by value), so n++ changes only the copy and a stays 5. "
      "addOneRef(int& n) takes a reference: n is another name (alias) for b itself, so n++ changes b to 6."),
    Q(F, "intermediate", C, "Default argument",
      """int area(int width, int height = 2) {
    return width * height;
}

int main() {
    std::cout << area(3) << " " << area(3, 4);
}""",
      "What is printed? Explain what = 2 in the parameter list means.",
      [("prints 6 12", ["6 12"], 2),
       ("height = 2 is a default argument used when the caller leaves it out", ["default", "left out", "leave it out", "omitted", "not passed", "missing"], 1),
       ("return sends width * height back to the caller", ["return", "sends back", "gives back"], 1)],
      [],
      "It prints 6 12. height = 2 is a default argument: area(3) leaves height out, so it is 2 and the function "
      "returns 3 * 2 = 6. area(3, 4) passes height explicitly, so the return value is 3 * 4 = 12."),
    Q(F, "intermediate", C, "Editing a std::string",
      """#include <iostream>
#include <string>

int main() {
    std::string word = "code";
    word[0] = 'm';
    word += "rn";
    std::cout << word << " " << word.size();
}""",
      "What is printed? Explain indexing, += and size().",
      [("prints modern 6", ["modern 6"], 2),
       ("word[0] is the first character (index 0) and can be changed", ["index 0", "first character", "first letter", "[0]"], 1),
       ("+= appends text; size() counts the characters", ["append", "adds", "count", "number of characters", "length"], 1)],
      [("thinks indexes start at 1", ["index 1 is the first", "starts at 1"], "Indexes start at 0, so word[0] is the c.")],
      "It prints modern 6. Indexes start at 0, so word[0] is the first character c, and assigning 'm' makes \"mode\". "
      "+= appends \"rn\" to give \"modern\". size() counts the characters: 6. Unlike string literals, std::string can "
      "be changed and grows as needed."),
    Q(F, "intermediate", C, "Growing a vector",
      """#include <iostream>
#include <vector>

int main() {
    std::vector<int> nums = {4, 7};
    nums.push_back(1);
    int total = 0;
    for (int n : nums) total += n;
    std::cout << total << " " << nums.size();
}""",
      "What is printed? Explain push_back and the range-based for loop.",
      [("prints 12 3", ["12 3"], 2),
       ("push_back adds 1 to the end, so the vector has 3 items", ["push_back", "end", "adds", "append"], 1),
       ("for (int n : nums) visits every element in turn", ["every element", "each element", "each item", "in turn", "range"], 1)],
      [],
      "It prints 12 3. A std::vector is a list that can grow. push_back(1) adds 1 to the end, so it holds {4, 7, 1}. "
      "The range-based for loop for (int n : nums) visits each element in turn, adding 4 + 7 + 1 = 12, and size() is "
      "3."),
    Q(F, "intermediate", C, "Breaking out early",
      """int sum = 0;
int i = 1;
while (true) {
    sum += i;
    if (sum > 10) break;
    i++;
}
std::cout << i << " " << sum;""",
      "What is printed? Trace sum and i, and explain break.",
      [("prints 5 15", ["5 15"], 2),
       ("sum goes 1, 3, 6, 10, 15", ["1, 3, 6, 10, 15", "1 3 6 10 15", "10, 15", "6, 10"], 1),
       ("break leaves the loop immediately, so i++ is skipped on the last pass", ["break", "leaves", "exits", "stops the loop"], 1)],
      [],
      "It prints 5 15. Trace it: sum goes 1, 3, 6, 10, 15 as i goes 1, 2, 3, 4, 5. When sum becomes 15 it is greater "
      "than 10, so break leaves the while (true) loop immediately and the last i++ is skipped, leaving i at 5."),
    Q(F, "intermediate", C, "Letters are numbers",
      """char c = 'A';
c = c + 2;
std::cout << c << " " << 'A' + 2;""",
      "What is printed? Why do the two outputs look so different?",
      [("prints C 67", ["c 67"], 2),
       ("a char stores a small number (the character code, A is 65)", ["65", "ascii", "character code", "number"], 1),
       ("'A' + 2 is an int, so cout prints the number; c is a char, so cout prints the letter", ["int", "integer", "promot"], 1)],
      [],
      "It prints C 67. A char stores a small number, the character code (ASCII), and 'A' is 65. c + 2 is 67, stored "
      "back in the char c, so cout prints the letter C. But 'A' + 2 on its own is promoted to an int, so cout prints "
      "the number 67."),
    Q(F, "intermediate", C, "Same name, inner block",
      """int x = 1;
{
    int x = 2;
    x = x + 10;
    std::cout << x << " ";
}
std::cout << x;""",
      "What is printed? Explain which x each line uses.",
      [("prints 12 1", ["12 1"], 2),
       ("the inner int x is a new variable that hides (shadows) the outer one", ["shadow", "hide", "new variable", "different variable", "separate"], 1),
       ("the inner x only exists inside its { } block (scope)", ["scope", "block", "inside the braces", "destroyed", "goes away"], 1)],
      [("thinks the outer x becomes 12", ["12 12"], "The inner declaration creates a separate variable; the outer x is never changed.")],
      "It prints 12 1. int x = 2 inside the braces declares a new variable that hides (shadows) the outer x. It only "
      "exists inside that { } block (its scope), so x = x + 10 makes the inner x 12. After the block it is gone, and "
      "the outer x is still 1."),
    Q(F, "intermediate", C, "Doubling a copy",
      """std::vector<int> v = {1, 2, 3};
for (int x : v) {
    x = x * 2;
}
for (int x : v) std::cout << x << " ";""",
      "The goal was to double every element. What is printed, and how do you fix it?",
      [("prints 1 2 3 (unchanged)", ["1 2 3", "unchanged", "not changed", "nothing changes"], 2),
       ("int x is a copy of each element, so changing x does not change v", ["copy", "copies"], 1),
       ("fix: use a reference, for (int& x : v)", ["int&", "int &", "auto&", "auto &", "reference"], 1)],
      [("thinks it prints 2 4 6", ["2 4 6"], "Each x is a fresh copy of the element; doubling the copy leaves the vector unchanged.")],
      "It prints 1 2 3, unchanged. In for (int x : v) each x is a copy of the element, so x = x * 2 only changes the "
      "copy. Use a reference, for (int& x : v) { x *= 2; }, so x refers to the real element, and it prints 2 4 6."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", C, "Following a pointer",
      """int a = 10;
int* p = &a;
*p = 20;
std::cout << a << " " << (p == &a);""",
      "What is printed? Explain &, int* and *p.",
      [("prints 20 1", ["20 1"], 2),
       ("&a is the address of a; p is a pointer that stores that address", ["address"], 1),
       ("*p follows the pointer (dereference), so *p = 20 changes a", ["dereferenc", "follows", "points to", "pointed"], 1)],
      [],
      "It prints 20 1. &a gives the address of a (where it lives in memory), and int* p is a pointer that stores that "
      "address. *p dereferences (follows) the pointer to the variable it points to, so *p = 20 changes a itself. p == "
      "&a is true, and cout prints true as 1."),
    Q(F, "advanced", C, "One past the end",
      """int marks[3] = {70, 85, 90};
for (int i = 0; i <= 3; i++) {
    std::cout << marks[i] << " ";
}""",
      "What is wrong with this loop, and what does C++ do about it?",
      [("i <= 3 reads marks[3], which is out of bounds (valid indexes are 0, 1, 2)", ["out of bounds", "out-of-bounds", "outside", "past the end", "marks[3]", "index 3"], 2),
       ("this is undefined behavior: C++ does not check, so it may print garbage or crash", ["undefined behavior", "undefined behaviour", "garbage", "no bounds check", "not checked", "crash"], 1),
       ("fix: use i < 3, or a std::vector / std::array with .at() or a range-for", ["i < 3", ".at(", "range-for", "range for", "std::array", "vector"], 1)],
      [("expects an error message", ["throws an exception", "index error", "indexerror"], "Plain arrays are not bounds-checked: C++ gives no error, the behaviour is simply undefined.")],
      "An array of 3 has valid indexes 0, 1 and 2, but i <= 3 also reads marks[3], which is out of bounds. C++ does "
      "not check plain array indexes, so this is undefined behavior: it might print a garbage number, crash, or seem "
      "fine. Fix the condition to i < 3, or use a range-for, or std::array/std::vector with .at(), which throws "
      "std::out_of_range."),
    Q(F, "advanced", C, "Copying a struct",
      """struct Point {
    int x;
    int y;
};

Point p{1, 2};
Point q = p;
q.x = 9;
std::cout << p.x << " " << q.x;""",
      "What is printed? Is q the same object as p?",
      [("prints 1 9", ["1 9"], 2),
       ("Point q = p makes an independent copy of every member", ["copy", "copies", "independent"], 1),
       ("C++ objects have value semantics (unlike references in Python/JS)", ["value semantic", "not the same object", "separate object", "different object", "not a reference"], 1)],
      [("thinks q is a reference to p", ["9 9"], "Assignment of a struct copies it; q is a separate object, so p.x stays 1.")],
      "It prints 1 9. Point q = p makes an independent copy of every member, because C++ objects have value semantics "
      "(unlike Python or JavaScript, where variables refer to the same object). q is a separate object, so changing "
      "q.x leaves p.x at 1. To share one object you would use a reference, Point& q = p."),
    Q(F, "advanced", C, "A tiny class",
      """class Counter {
    int count = 0;
public:
    void add() { count++; }
    int get() const { return count; }
};

Counter c;
c.add();
c.add();
std::cout << c.get();
// std::cout << c.count;  // what if we uncomment this?""",
      "What is printed? What happens if the commented line is uncommented, and why?",
      [("prints 2", ["prints 2", "output is 2", "it prints 2", "2 is printed"], 2),
       ("count is private (the default in a class), so c.count is a compile error", ["private", "compile error", "not accessible", "inaccessible"], 1),
       ("public methods like add and get are the only way in (encapsulation); const means get doesn't change the object", ["public", "encapsulat", "const"], 1)],
      [],
      "It prints 2: add() is called twice, so count goes 0 → 1 → 2 and get() returns it. Members of a class are "
      "private by default, so uncommenting c.count is a compile error: outside code may only use the public methods "
      "(encapsulation). The const on get() promises it will not change the object."),
    Q(F, "advanced", C, "Changing a constant",
      """const int maxPlayers = 4;
maxPlayers = 5;
std::cout << maxPlayers;""",
      "What happens? Why would anyone want this behaviour?",
      [("compile error: a const variable cannot be assigned after it is created", ["compile error", "compiler error", "cannot be assigned", "cannot be changed", "can't be changed", "read-only", "read only"], 2),
       ("const protects values that must not change and documents intent", ["protect", "mistake", "intent", "never change", "accident"], 1)],
      [("thinks it prints 5", ["prints 5"], "The program never runs: the compiler rejects the assignment to a const variable.")],
      "It does not compile: maxPlayers is const, so it cannot be assigned after it is created, and the compiler "
      "reports an error (assignment of read-only variable). That is the point of const: the compiler protects values "
      "that must never change from accidental edits and documents your intent."),
    Q(F, "advanced", C, "Pointer to nothing",
      """int* p = nullptr;
if (p != nullptr) {
    std::cout << *p;
} else {
    std::cout << "no value";
}""",
      "What is printed? What would happen without the if check?",
      [("prints no value", ["no value"], 2),
       ("nullptr means the pointer points to nothing", ["points to nothing", "nothing", "no object", "null pointer", "empty"], 1),
       ("dereferencing nullptr (*p) is undefined behavior, often a crash (segfault)", ["undefined behavior", "undefined behaviour", "crash", "segfault", "segmentation"], 1)],
      [],
      "It prints no value. nullptr means the pointer points to nothing, so the check sends us to the else. Without it, "
      "*p would dereference a null pointer: that is undefined behavior and usually crashes the program "
      "(segmentation fault). Always check a pointer that might be null before using it."),
    Q(F, "advanced", C, "Too big for an int",
      """#include <climits>

int big = INT_MAX;   // 2147483647
long long safe = INT_MAX;
safe = safe + 1;
big = big + 1;""",
      "What is safe after the code runs? What about big, and why is it a problem?",
      [("safe is 2147483648 because long long has room for it", ["2147483648", "long long"], 2),
       ("big + 1 overflows a signed int, which is undefined behavior", ["overflow", "undefined behavior", "undefined behaviour"], 1),
       ("the result often wraps to a negative number, but C++ does not promise anything", ["negative", "wrap", "-2147483648", "no guarantee", "not guaranteed"], 1)],
      [("thinks big becomes 2147483648", ["big is 2147483648", "big becomes 2147483648"], "An int cannot hold 2147483648; INT_MAX + 1 overflows.")],
      "safe is 2147483648, because long long (64-bit) has room for it. An int usually holds at most 2147483647 "
      "(INT_MAX), so big + 1 overflows a signed int, which is undefined behavior: in practice it often wraps to a "
      "negative number (-2147483648), but C++ guarantees nothing. Use a wider type such as long long when values can "
      "get large."),
    Q(F, "advanced", C, "Counting words with a map",
      """#include <iostream>
#include <map>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words = {"pear", "apple", "pear"};
    std::map<std::string, int> counts;
    for (const auto& w : words) counts[w]++;
    for (const auto& [word, n] : counts)
        std::cout << word << "=" << n << " ";
}""",
      "What is printed, and in what order? Explain counts[w]++.",
      [("prints apple=1 pear=2", ["apple=1 pear=2"], 2),
       ("counts[w] creates a missing key with value 0, then ++ adds one", ["creates", "inserts", "starts at 0", "default", "value 0", "zero"], 1),
       ("std::map keeps keys sorted, so apple comes before pear", ["sorted", "alphabetical", "order"], 1)],
      [("expects insertion order", ["pear=2 apple=1"], "std::map orders keys by comparison (alphabetically for strings), not by insertion.")],
      "It prints apple=1 pear=2. counts[w] looks up the key and, if it is missing, creates it with value 0 (default), "
      "then ++ adds one. So pear ends at 2 and apple at 1. std::map keeps its keys sorted (alphabetical for strings), "
      "so apple is printed first even though pear was seen first."),
]
