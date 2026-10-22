"""Fundamentals: PHP — first steps for complete beginners."""

from app.content.qdef import Q

F, P = "fundamentals", "php"

QUESTIONS_FUND_PHP = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", P, "Single or double quotes",
      """<?php
$name = "Sam";
echo "Hello, " . $name . "!";
echo 'Hi $name';
echo "Hi $name";""",
      "What exactly is printed? Explain the dot and the two kinds of quotes.",
      [("single quotes print $name literally; double quotes insert the value", ["single quote", "literal", "interpolat", "as is", "as-is"], 2),
       ("the dot joins (concatenates) strings", ["concaten", "join", "dot"], 1),
       ("echo adds no newline, so it runs together: Hello, Sam!Hi $nameHi Sam", ["newline", "together", "no space", "line break", "same line"], 1)],
      [],
      "It prints Hello, Sam!Hi $nameHi Sam all on one line, because echo adds no newline. The dot joins "
      "(concatenates) strings. Inside single quotes $name is printed literally; inside double quotes PHP inserts "
      "(interpolates) the value, Sam."),
    Q(F, "beginner", P, "Forgotten dollar sign",
      """<?php
$count = 3;
count = count + 1;
echo $count;""",
      "This does not run. What is wrong, and how do you fix it?",
      [("syntax/parse error: PHP variables must start with $", ["syntax error", "parse error", "parseerror", "missing $", "without $", "need $", "needs $", "must start with $", "missing the $", "forgot the $", "no $"], 2),
       ("fix: $count = $count + 1 (or $count++)", ["$count = $count + 1", "$count++", "$count += 1"], 1)],
      [],
      "It is a syntax (parse) error: every PHP variable must start with $, and line 3 is missing the $ on count. "
      "Write $count = $count + 1; (or $count++), and then it prints 4."),
    Q(F, "beginner", P, "Dividing in PHP",
      """<?php
echo 7 / 2, " ", intdiv(7, 2), " ", 7 % 2, " ", 2 ** 3;""",
      "What is printed? Explain each operator.",
      [("prints 3.5 3 1 8", ["3.5 3 1 8"], 2),
       ("/ gives 3.5; intdiv is whole-number division; % is the remainder; ** is power",
        ["intdiv", "remainder", "power"], 1)],
      [],
      "It prints 3.5 3 1 8. / gives a decimal (3.5) when it doesn't divide evenly. intdiv does whole-number "
      "division (3). % is the remainder (1). ** raises to a power: 2 × 2 × 2 = 8."),
    Q(F, "beginner", P, "Mild weather",
      """<?php
$temp = 18;
if ($temp > 25) {
    echo "hot";
} elseif ($temp > 15) {
    echo "mild";
} else {
    echo "cold";
}""",
      "What is printed, and how does PHP choose the branch?",
      [("prints mild", ["mild"], 2),
       ("conditions are checked top to bottom and only the first true branch runs", ["first", "top to bottom", "in order", "only one"], 1)],
      [],
      "It prints mild. PHP checks the conditions from top to bottom: 18 > 25 is false, 18 > 15 is true, so it "
      "runs only that first true branch and skips the else."),
    Q(F, "beginner", P, "Counting from zero",
      """<?php
for ($i = 0; $i < 4; $i++) {
    echo $i;
}""",
      "What is printed? Why does the loop run exactly 4 times?",
      [("prints 0123", ["0123", "0 1 2 3", "0, 1, 2, 3"], 2),
       ("it starts at 0 and stops when $i reaches 4 because the test is < 4", ["< 4", "reaches 4", "stops", "not <="], 1)],
      [],
      "It prints 0123 (echo adds no spaces). $i starts at 0 and goes up by 1; when $i reaches 4 the test $i < 4 "
      "is false and the loop stops, so it runs for 0, 1, 2, 3: four times."),
    Q(F, "beginner", P, "Adding to an array",
      """<?php
$colors = ["red", "green"];
$colors[] = "blue";
echo count($colors), " ", $colors[0], " ", $colors[2];""",
      "What is printed? What does $colors[] = do?",
      [("prints 3 red blue", ["3 red blue"], 2),
       ("[] = appends to the end; indexes start at 0", ["append", "end", "start at 0", "zero"], 1)],
      [],
      "It prints 3 red blue. $colors[] = \"blue\" appends to the end of the array, so there are 3 items. Indexes "
      "start at 0: [0] is red and [2] is blue."),
    Q(F, "beginner", P, "echo versus print",
      """<?php
$r = print "A";
echo $r;
echo "B", "C";""",
      "What is printed? How are echo and print different?",
      [("prints A1BC", ["a1bc"], 2),
       ("print returns 1 and takes one value; echo returns nothing and can take several separated by commas",
        ["returns 1", "return 1", "several", "multiple", "comma"], 1)],
      [],
      "It prints A1BC. print outputs A and returns 1, which is stored in $r and echoed. echo returns nothing but "
      "can take several values separated by commas, so it prints B and C."),
    Q(F, "beginner", P, "Default parameter",
      """<?php
function area($w, $h = 2) {
    return $w * $h;
}
echo area(3), " ", area(3, 4);""",
      "What is printed? What does $h = 2 mean?",
      [("prints 6 12", ["6 12", "6 and 12", "6, 12"], 2),
       ("$h defaults to 2 when no second argument is passed", ["default"], 1)],
      [],
      "It prints 6 12. $h = 2 is a default value: area(3) does not pass $h, so it uses 2 and returns 6. area(3, 4) "
      "passes 4, so it returns 12."),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", P, "Associative array loop",
      """<?php
$ages = ["ann" => 31, "bo" => 25];
$ages["cy"] = 40;
foreach ($ages as $name => $age) {
    echo "$name:$age ";
}
echo isset($ages["dee"]) ? "yes" : "no";""",
      "What is printed?",
      [("prints ann:31 bo:25 cy:40 no", ["ann:31 bo:25 cy:40"], 2),
       ("keys keep insertion order; isset is false for a missing key", ["isset", "missing", "insertion order", "order"], 1)],
      [],
      "It prints ann:31 bo:25 cy:40 no. Associative arrays keep insertion order, so cy comes last. foreach gives "
      "each key and value. isset is false for the missing key dee, so the ternary prints no."),
    Q(F, "intermediate", P, "Loose comparisons",
      """<?php
var_dump(0 == "a");
var_dump("1" == "01");
var_dump(100 == "1e2");
var_dump("abc" === "abc");""",
      "Predict the four results (PHP 8).",
      [("false, true, true, true", ["false true true true", "false, true, true, true"], 2),
       ("numeric strings are compared as numbers with ==; PHP 8 compares a number and a non-numeric string as strings",
        ["numeric"], 1)],
      [],
      "It prints bool(false), bool(true), bool(true), bool(true) — false, true, true, true. In PHP 8, 0 == \"a\" "
      "compares as strings, so it is false. \"1\" and \"01\", and 100 and \"1e2\", are numeric strings, so == "
      "compares them as numbers. === needs the same type and value."),
    Q(F, "intermediate", P, "String functions",
      """<?php
$s = "Hello World";
echo strlen($s), "|", strtoupper($s), "|", substr($s, 0, 5), "|", str_replace("World", "PHP", $s);""",
      "What is printed between the bars?",
      [("strlen is 11 (the space counts)", ["11"], 1),
       ("strtoupper gives HELLO WORLD", ["uppercase", "upper case", "capital", "strtoupper"], 1),
       ("substr($s, 0, 5) takes 5 characters from index 0: Hello", ["5 characters", "five characters", "first 5", "first five"], 1),
       ("str_replace gives Hello PHP", ["hello php"], 1)],
      [],
      "It prints 11|HELLO WORLD|Hello|Hello PHP. strlen counts 11 characters including the space; strtoupper makes "
      "it uppercase; substr takes the first 5 characters starting at index 0; str_replace swaps World for PHP."),
    Q(F, "intermediate", P, "Casting values",
      """<?php
var_dump((bool) "0");
var_dump((int) "12abc");
var_dump("10" + 5);
var_dump((string) false);""",
      "Predict all four results. Which one surprises people?",
      [("(bool) \"0\" is false: the string \"0\" is falsy in PHP", ["falsy", "is false", "bool(false)"], 2),
       ("(int) \"12abc\" reads the leading digits: 12; \"10\" + 5 is 15", ["12"], 1),
       ("false as a string is the empty string", ["empty"], 1)],
      [],
      "It prints bool(false), int(12), int(15), string(0) \"\". The string \"0\" is falsy in PHP, so (bool) \"0\" is "
      "false. (int) reads the leading digits 12. \"10\" + 5 converts to numbers: 15. false becomes the empty string."),
    Q(F, "intermediate", P, "match is strict",
      """<?php
$code = "2";
echo match($code) {
    2 => "two",
    "2" => "string two",
    default => "other",
};""",
      "What is printed? How is match different from switch?",
      [("prints string two", ["string two"], 2),
       ("match compares strictly (===), while switch uses loose ==", ["strict", "==="], 1)],
      [("thinks it prints two", ["prints two", "outputs two", "just two"], "match uses ===, so the string \"2\" does not match the integer 2.")],
      "It prints string two. match compares strictly with ===, so the string \"2\" does not match the integer 2 and "
      "goes to the \"2\" arm. A switch would use loose == and pick the first case."),
    Q(F, "intermediate", P, "Function cannot see outside",
      """<?php
$total = 10;
function addTax() {
    return $total * 1.2;
}
echo addTax();""",
      "Expected 12. What actually happens, and how do you fix it?",
      [("functions can't see variables from outside: $total is undefined inside (warning)",
        ["undefined", "not visible", "can't see", "cannot see", "not accessible", "outside"], 2),
       ("the result is 0", ["prints 0", "0 is printed", "outputs 0", "result is 0", "returns 0"], 1),
       ("fix: pass $total as a parameter", ["parameter", "argument", "global"], 1)],
      [],
      "Functions can't see variables from outside them, so inside addTax $total is undefined: PHP warns, treats it "
      "as null, and the result is 0. Pass it in: function addTax($total) { ... } and call addTax($total)."),
    Q(F, "intermediate", P, "Null coalescing",
      """<?php
$user = ["name" => "Kim"];
echo $user["email"] ?? "no email", " ";
echo is_null($user["name"] ?? null) ? "null" : "set";""",
      "What is printed? What does ?? do?",
      [("prints no email set", ["no email"], 2),
       ("?? uses the right side when the left is null or missing, without a warning", ["missing", "null", "warning"], 1)],
      [],
      "It prints no email set. ?? returns the left side if it exists and is not null; otherwise the right side. "
      "email is missing, so no email is used, with no warning. name exists, so it is not null and set is printed."),
    Q(F, "intermediate", P, "Throw skips the rest",
      """<?php
function divide($a, $b) {
    if ($b === 0) {
        throw new InvalidArgumentException("b must not be 0");
    }
    return $a / $b;
}
try {
    echo divide(10, 2), " ";
    echo divide(1, 0), " ";
    echo "after";
} catch (InvalidArgumentException $e) {
    echo "Error: ", $e->getMessage();
}""",
      "What is printed? Does after appear?",
      [("prints 5 then Error: b must not be 0", ["must not be 0"], 2),
       ("throw jumps straight to catch, so after never prints", ["never", "skip", "not printed", "doesn't print", "does not print", "jumps"], 1)],
      [],
      "It prints 5 Error: b must not be 0. divide(10, 2) returns 5. divide(1, 0) throws, which jumps straight to "
      "the catch block, so the rest of the try block is skipped and after never prints."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", P, "foreach by reference",
      """<?php
$nums = [1, 2, 3];
foreach ($nums as &$n) {
    $n = $n * 2;
}
foreach ($nums as $n) {}
print_r($nums);""",
      "Expected [2, 4, 6]. What is printed, and why?",
      [("prints [2, 4, 4]", ["2, 4, 4", "2 4 4"], 2),
       ("$n stays a reference to the last element, and the second loop writes into it; unset($n) after the first loop",
        ["reference", "unset"], 1)],
      [],
      "It prints 2, 4, 4. After the first loop, $n is still a reference to the last element. The second foreach "
      "assigns each value to $n, which overwrites the last element; on its final step it copies 4 into it. Call "
      "unset($n) after a by-reference loop."),
    Q(F, "advanced", P, "Arrays are copied",
      """<?php
$a = [1, 2];
$b = $a;
$b[] = 3;
echo count($a), count($b);""",
      "What is printed? Does changing $b change $a?",
      [("prints 23", ["23", "2 and 3", "2 3"], 2),
       ("arrays are assigned by value (a copy), unlike objects", ["copy", "value"], 1)],
      [],
      "It prints 23. In PHP, arrays are assigned by value: $b = $a makes a copy (copy-on-write), so appending to $b "
      "leaves $a with 2 items. Objects behave differently: they are shared."),
    Q(F, "advanced", P, "Dot and plus together",
      """<?php
$a = 2;
echo "Sum: " . $a + 3;""",
      "What does PHP 8 print, and why? How would you write it clearly?",
      [("prints Sum: 5", ["sum: 5"], 2),
       ("in PHP 8, + binds tighter than ., so $a + 3 is computed first; add parentheses",
        ["precedence", "first", "parenthes", "tighter"], 1)],
      [],
      "PHP 8 prints Sum: 5. Arithmetic + has higher precedence than the . operator, so $a + 3 is computed first "
      "and then joined. (Older PHP did it left to right.) Write \"Sum: \" . ($a + 3) with parentheses to be clear."),
    Q(F, "advanced", P, "Strict types",
      """<?php
declare(strict_types=1);
function square(int $x): int {
    return $x * $x;
}
echo square(3), " ";
echo square("4");""",
      "What is printed, and what happens on the last line?",
      [("prints 9, then throws a TypeError for \"4\"", ["typeerror", "type error"], 2),
       ("strict_types turns off automatic conversion of \"4\" to an int", ["strict", "coerc", "convert"], 1)],
      [],
      "It prints 9 and then throws a TypeError. With declare(strict_types=1), PHP no longer converts the string "
      "\"4\" to an int automatically, so passing a string to an int parameter is an error."),
    Q(F, "advanced", P, "One step too many",
      """<?php
$items = ["a", "b", "c"];
$i = 0;
while ($i <= count($items)) {
    echo $items[$i] ?? "?";
    $i++;
}""",
      "What is printed? What is the bug?",
      [("prints abc?", ["abc?"], 2),
       ("<= runs 4 times; index 3 doesn't exist, so ?? prints ?; use <", ["4 times", "four times", "index 3", "<="], 1)],
      [],
      "It prints abc?. The condition uses <=, so the loop runs 4 times (0 to 3), but index 3 doesn't exist; ?? "
      "turns the missing value into ?. Use $i < count($items), or a foreach."),
    Q(F, "advanced", P, "static counter",
      """<?php
function counter() {
    static $n = 0;
    $n++;
    return $n;
}
echo counter(), counter(), counter();""",
      "What is printed? What does static do?",
      [("prints 123", ["123", "1 2 3", "1, 2, 3"], 2),
       ("static keeps its value between calls and is initialised only once", ["keep", "between calls", "once", "remember"], 1)],
      [],
      "It prints 123. A static variable is initialised only once and keeps its value between calls, so $n goes "
      "1, 2, 3 instead of resetting to 0."),
    Q(F, "advanced", P, "empty() and zero",
      """<?php
$qty = "0";
if (empty($qty)) {
    echo "Please enter a quantity";
} else {
    echo "Ordering $qty";
}""",
      "The user typed 0. What is printed? How would you check correctly?",
      [("prints Please enter a quantity", ["please enter"], 2),
       ("empty() treats the string \"0\" as empty (falsy); check $qty === \"\" or use is_numeric",
        ["falsy", "is_numeric", "=== \"\"", "=== ''"], 1)],
      [],
      "It prints Please enter a quantity. empty() is true for falsy values, and the string \"0\" is falsy, so a "
      "real answer of 0 looks empty. Check $qty === \"\" for missing input, or use is_numeric($qty)."),
    Q(F, "advanced", P, "false equals null",
      """<?php
$config = ["debug" => false];
if ($config["debug"] == null) {
    echo "debug not set";
} else {
    echo "debug is set";
}""",
      "debug IS set (to false). What is printed? Fix the check.",
      [("prints debug not set", ["debug not set"], 2),
       ("false == null is true with loose comparison; use array_key_exists or ===",
        ["loose", "===", "array_key_exists", "isset"], 1)],
      [],
      "It prints debug not set. With loose comparison, false == null is true. To ask whether the key exists, use "
      "array_key_exists(\"debug\", $config); to test for null specifically, use === null."),
]
