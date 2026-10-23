"""Looping drills for every programming language: for, while, do-while, nested loops,
break/continue, "what does this print" tracing and off-by-one bugs."""

from app.content.qdef import Q

F = "fundamentals"

QUESTIONS_LOOPS = [
    # ── Python ──────────────────────────────────────────────────────────────
    Q(F, "beginner", "python", "Counting down with a step",
      """for i in range(10, 0, -3):
    print(i, end=" ")""",
      "What is printed? Explain the three numbers given to range.",
      [("prints 10 7 4 1", ["10 7 4 1"], 2),
       ("range(start, stop, step): start at 10, go down by 3", ["start", "step", "down by 3", "-3"], 1),
       ("the stop value 0 is never included", ["never included", "not included", "excluded", "stops before", "before 0"], 1)],
      [("thinks 0 or -2 is printed", ["10 7 4 1 -2", "10 7 4 1 0"], "range stops before reaching the stop value, so nothing at or below 0 is produced.")],
      "It prints 10 7 4 1. range(10, 0, -3) means start at 10 and add the step -3 each time (go down by 3): 10, 7, 4, "
      "1. The stop value 0 is never included, and the next value -2 is already past it, so the loop ends."),
    Q(F, "beginner", "python", "While loop countdown",
      """n = 3
while n > 0:
    print(n)
    n -= 1
print("liftoff")""",
      "What is printed, line by line? What would happen without n -= 1?",
      [("prints 3, 2, 1 and then liftoff", ["3 2 1 liftoff", "3, 2, 1, liftoff", "3 2 1 and liftoff", "3, 2, 1 and liftoff"], 2),
       ("the condition n > 0 is checked before every pass; when n is 0 the loop ends", ["checked before", "before every", "n is 0", "becomes 0", "reaches 0", "is false"], 1),
       ("without n -= 1 the condition never becomes false: an infinite loop", ["infinite", "forever", "never ends", "never stops"], 1)],
      [],
      "It prints 3, 2, 1 and liftoff, each on its own line. The condition n > 0 is checked before every pass: n goes "
      "3 → 2 → 1 → 0, and when n becomes 0 the condition is false, so the loop ends and liftoff prints. Without "
      "n -= 1, n stays 3 and the loop never ends (an infinite loop)."),
    Q("code_tracing", "intermediate", "python", "Skipping and stopping",
      """for i in range(10):
    if i % 2 == 0:
        continue
    if i > 6:
        break
    print(i, end=" ")""",
      "What is printed? Explain what continue and break each do here.",
      [("prints 1 3 5", ["1 3 5"], 2),
       ("continue skips the rest of this pass for even numbers", ["continue skips", "skip", "next pass", "next iteration"], 1),
       ("break ends the whole loop at 7, so 7 and 9 are never printed", ["break ends", "ends the loop", "exits", "stops the loop", "at 7"], 1)],
      [("thinks break only skips 7", ["1 3 5 9"], "break leaves the loop completely; the loop never reaches 9.")],
      "It prints 1 3 5. For even numbers continue skips the rest of that pass and goes to the next iteration, so only "
      "odd numbers reach the second if. At i = 7, 7 > 6 is true and break ends the whole loop, so 7 and 9 are never "
      "printed."),
    Q("debugging", "intermediate", "python", "Sum that stops one short",
      """# Goal: add the numbers 1 to 5 (expected 15)
i = 1
total = 0
while i < 5:
    total += i
    i += 1
print(total)""",
      "It prints 10, not 15. Find the off-by-one bug and fix it.",
      [("i < 5 stops before adding 5, so the result is 1+2+3+4 = 10", ["i < 5", "before adding 5", "never adds 5", "1+2+3+4", "1 + 2 + 3 + 4", "off-by-one", "off by one"], 2),
       ("fix: while i <= 5 (or sum(range(1, 6)))", ["i <= 5", "range(1, 6)"], 1)],
      [],
      "It is an off-by-one bug: the condition i < 5 is false as soon as i reaches 5, so the loop stops before adding 5 "
      "and computes 1 + 2 + 3 + 4 = 10. Use while i <= 5 (or simply sum(range(1, 6))) to include 5 and get 15."),
    Q("code_tracing", "advanced", "python", "Break inside a nested loop",
      """for i in range(3):
    for j in range(3):
        if j == i:
            break
        print(i, j)""",
      "What is printed? Which loop does break leave?",
      [("prints 1 0, 2 0, 2 1 (three lines)", ["1 0, 2 0 and 2 1", "1 0, 2 0, 2 1", "1 0 2 0 2 1", "(1, 0), (2, 0), (2, 1)"], 2),
       ("break only leaves the inner loop; the outer loop carries on", ["inner loop", "innermost", "only the inner", "outer loop continues", "outer loop carries on"], 1),
       ("for i = 0 the inner loop breaks immediately, so nothing prints", ["i = 0", "immediately", "nothing prints", "prints nothing"], 1)],
      [("thinks break ends both loops", ["only 1 0", "stops everything"], "break exits only the loop it is directly inside.")],
      "It prints three lines: 1 0, 2 0 and 2 1. break only leaves the inner loop; the outer loop carries on with the "
      "next i. For i = 0, j == i at once, so it breaks immediately and nothing prints. For i = 1 it prints j = 0 then "
      "breaks at j = 1. For i = 2 it prints j = 0 and 1, then breaks at j = 2."),
    Q("code_tracing", "advanced", "python", "The loop's else clause",
      """for n in [3, 5, 7]:
    if n % 2 == 0:
        print("found even", n)
        break
else:
    print("no even number")""",
      "What is printed? When does the else of a for loop run?",
      [("prints no even number", ["no even number"], 2),
       ("a for loop's else runs only when the loop finishes without break", ["without break", "no break", "never breaks", "didn't break", "did not break", "finishes normally"], 2)],
      [("thinks else pairs with the if", ["else of the if", "belongs to the if"], "The else is aligned with for, not if: it is the loop's else clause.")],
      "It prints no even number. The else is aligned with the for, so it is the loop's else clause: it runs only when "
      "the loop finishes normally, without break. None of 3, 5, 7 is even, break never runs, so the else runs. With "
      "[3, 4] it would print found even 4 and skip the else."),

    # ── JavaScript ──────────────────────────────────────────────────────────
    Q(F, "beginner", "javascript", "do...while runs at least once",
      """let n = 10;
do {
  console.log(n);
  n++;
} while (n < 5);""",
      "How many times does the body run, and what is printed? Compare with a plain while loop.",
      [("prints 10 once", ["10 once", "once", "one time", "1 time"], 2),
       ("do...while checks the condition after the body, so it always runs at least once", ["after the body", "at least once", "checked after", "checks after", "end of"], 1),
       ("a while (n < 5) loop would print nothing because 10 < 5 is false at the start", ["nothing", "never runs", "zero times", "0 times", "is false"], 1)],
      [],
      "It prints 10 once. do...while checks its condition after the body, so the body always runs at least once: it "
      "prints 10, n becomes 11, then 11 < 5 is false and the loop stops. A plain while (n < 5) checks first, and "
      "since 10 < 5 is false it would print nothing (run zero times)."),
    Q(F, "beginner", "javascript", "Counting by twos",
      """for (let i = 0; i <= 8; i += 2) {
  console.log(i);
}""",
      "What is printed and how many numbers is that? Explain i += 2 and <=.",
      [("prints 0 2 4 6 8 (five numbers)", ["0 2 4 6 8", "0, 2, 4, 6, 8"], 2),
       ("i += 2 adds two after each pass", ["adds two", "adds 2", "add 2", "by 2", "by two"], 1),
       ("<= 8 includes 8; the loop stops at 10", ["includes 8", "at 10", "becomes 10", "10 <= 8"], 1)],
      [],
      "It prints 0 2 4 6 8, five numbers. i starts at 0 and i += 2 adds two after each pass. The condition i <= 8 "
      "includes 8; when i becomes 10, 10 <= 8 is false and the loop stops."),
    Q("code_tracing", "intermediate", "javascript", "for...in versus for...of",
      """const a = [10, 20];
let s = "";
for (const k in a) s += k;
for (const v of a) s += v;
console.log(s);""",
      "What is printed? Explain the difference between for...in and for...of.",
      [("prints 011020", ["011020"], 2),
       ("for...in loops over the keys (indexes as strings \"0\", \"1\")", ["keys", "indexes", "indices", "index"], 1),
       ("for...of loops over the values 10 and 20", ["values"], 1)],
      [("thinks for...in gives the values", ["10201020"], "for...in iterates property keys; for arrays that is the indexes, as strings.")],
      "It prints 011020. for...in loops over the keys of the array, its indexes as strings \"0\" and \"1\", so s "
      "becomes \"01\". for...of loops over the values 10 and 20, which are appended as text: \"011020\". Use for...of "
      "(or forEach) for array values."),
    Q("debugging", "intermediate", "javascript", "The loop that never ends",
      """let i = 0;
while (i < 3) {
  console.log("step", i);
}
i++;""",
      "This freezes the browser tab. Why, and how do you fix it?",
      [("i++ is outside the loop, so i stays 0 and i < 3 is always true: infinite loop", ["infinite", "never ends", "forever", "always true", "outside the loop"], 2),
       ("fix: move i++ inside the braces (or use a for loop)", ["inside", "for (let i", "for loop", "move"], 1)],
      [],
      "i++ is after the closing brace, outside the loop, so i stays 0 and i < 3 is always true: an infinite loop that "
      "prints step 0 forever and freezes the tab. Move i++ inside the braces, or write for (let i = 0; i < 3; i++), "
      "which keeps the counter update next to the condition."),
    Q("code_tracing", "advanced", "javascript", "Breaking out of both loops",
      """outer: for (let i = 0; i < 3; i++) {
  for (let j = 0; j < 3; j++) {
    if (i * j === 2) break outer;
    console.log(i, j);
  }
}""",
      "What is printed? What does break outer do that a plain break would not?",
      [("prints 0 0, 0 1, 0 2, 1 0, 1 1 and then stops", ["0 0, 0 1, 0 2, 1 0, 1 1", "0 0 0 1 0 2 1 0 1 1"], 2),
       ("at i = 1, j = 2 the product is 2 and break outer leaves both loops", ["both loops", "outer loop", "i = 1, j = 2", "labeled", "label"], 1),
       ("a plain break would only leave the inner loop and i = 2 would run", ["only the inner", "plain break", "i = 2"], 1)],
      [],
      "It prints 0 0, 0 1, 0 2, 1 0, 1 1 and then stops. When i = 1, j = 2 the product is 2, so break outer runs: the "
      "label names the outer loop, so it leaves both loops at once. A plain break would only leave the inner loop and "
      "i = 2 would still run (printing 2 0)."),
    Q("debugging", "advanced", "javascript", "Removing items while looping forward",
      """const xs = [1, 2, 2, 3];
for (let i = 0; i < xs.length; i++) {
  if (xs[i] === 2) xs.splice(i, 1);
}
console.log(xs);""",
      "The goal was to remove every 2. What is printed, why, and how do you fix it?",
      [("prints [1, 2, 3]: one 2 survives", ["[1, 2, 3]", "[1,2,3]", "one 2 survives", "one 2 is left"], 2),
       ("splice shifts the later items left, then i++ skips the item that moved into position i", ["shift", "skip", "moves left", "moved"], 1),
       ("fix: xs.filter(x => x !== 2), or loop backwards, or only i++ when nothing was removed", ["filter", "backwards", "from the end", "i--"], 1)],
      [],
      "It prints [1, 2, 3]: one 2 survives. At i = 1 splice removes the first 2 and shifts the later items left, so the "
      "second 2 moves into index 1; then i++ moves on to index 2 and skips it. Use xs = xs.filter(x => x !== 2), loop "
      "backwards from the end, or i-- after each splice."),

    # ── PHP ─────────────────────────────────────────────────────────────────
    Q(F, "beginner", "php", "A for loop with commas",
      """<?php
for ($i = 1; $i <= 3; $i++) {
    echo $i . ",";
}""",
      "What exactly is printed? Explain each part of the for header.",
      [("prints 1,2,3, (with a trailing comma)", ["1,2,3,"], 2),
       ("$i = 1 runs once; $i <= 3 is checked before each pass; $i++ adds one after it", ["once", "before each", "adds one", "add 1", "after each"], 1),
       ("the dot joins the number and the comma", ["dot", "join", "concaten"], 1)],
      [],
      "It prints 1,2,3, with a trailing comma. $i = 1 runs once at the start, $i <= 3 is checked before each pass, and "
      "$i++ adds one after each pass, so the body runs for 1, 2 and 3. The dot joins (concatenates) the number and "
      "the comma. implode(\",\", range(1, 3)) avoids the trailing comma."),
    Q(F, "beginner", "php", "do-while in PHP",
      """<?php
$tries = 0;
do {
    $tries++;
    echo "Attempt $tries\\n";
} while ($tries < 3);""",
      "What is printed? Why is do-while a good fit for “try at least once”?",
      [("prints Attempt 1, Attempt 2, Attempt 3", ["attempt 1, attempt 2, attempt 3", "attempt 1 attempt 2 attempt 3", "attempt 1 to attempt 3"], 2),
       ("the condition is checked after the body, so the body runs at least once", ["after the body", "at least once", "checked after"], 1),
       ("it stops when $tries reaches 3 because 3 < 3 is false", ["3 < 3", "reaches 3", "is false"], 1)],
      [],
      "It prints Attempt 1, Attempt 2, Attempt 3, one per line. do-while checks its condition after the body, so the "
      "body runs at least once, which suits “try first, then decide whether to retry”. When $tries reaches 3, 3 < 3 "
      "is false and the loop stops."),
    Q("code_tracing", "intermediate", "php", "continue 2 in nested loops",
      """<?php
foreach ([1, 2, 3] as $a) {
    foreach ([1, 2, 3] as $b) {
        if ($b > $a) continue 2;
        echo "$a$b ";
    }
}""",
      "What is printed? What does the 2 in continue 2 mean?",
      [("prints 11 21 22 31 32 33", ["11 21 22 31 32 33"], 2),
       ("continue 2 skips to the next pass of the outer loop (two levels up)", ["outer loop", "two levels", "2 levels", "next $a", "enclosing"], 1),
       ("so for each $a only $b values up to $a are printed", ["up to $a", "$b <= $a", "less than or equal"], 1)],
      [],
      "It prints 11 21 22 31 32 33. continue 2 means continue the loop two levels up, i.e. jump straight to the next "
      "pass of the outer loop (the next $a). As soon as $b > $a the rest of the inner loop is abandoned, so for each "
      "$a only the $b values up to $a ($b <= $a) are printed."),
    Q("debugging", "intermediate", "php", "One past the last name",
      """<?php
$names = ["Ana", "Ben", "Cy"];
for ($i = 0; $i <= count($names); $i++) {
    echo $names[$i], "\\n";
}""",
      "The output ends with a warning. Find the off-by-one bug and give two fixes.",
      [("$i <= count reaches index 3, which does not exist: Warning: Undefined array key 3", ["undefined array key", "undefined offset", "index 3", "does not exist", "off-by-one", "off by one"], 2),
       ("fix: $i < count($names)", ["$i < count"], 1),
       ("or use foreach ($names as $name)", ["foreach"], 1)],
      [],
      "It is an off-by-one bug: indexes run 0 to 2, but $i <= count($names) also runs $i = 3, an index that does not "
      "exist, so PHP prints Warning: Undefined array key 3 (and an empty line). Use $i < count($names), or better "
      "foreach ($names as $name), which cannot go past the end."),
    Q("code_tracing", "advanced", "php", "Building a string backwards",
      """<?php
$s = "";
for ($i = 5; $i > 0; $i -= 2) {
    $s = $i . $s;
}
echo $s;""",
      "What is printed? Trace $i and $s on every pass.",
      [("prints 135", ["prints 135", "output is 135", "it prints 135", "\"135\""], 2),
       ("$i takes 5, 3, 1 and the loop stops at -1", ["5, 3, 1", "5 3 1", "-1"], 1),
       ("each new number goes in front ($i . $s), so the order is reversed", ["in front", "prepend", "before", "reversed"], 1)],
      [],
      "It prints 135. $i takes the values 5, 3, 1, and then -1 fails $i > 0 and the loop stops. $s = $i . $s puts each "
      "new number in front (prepends it): \"5\", then \"35\", then \"135\", so the order is reversed compared with "
      "the loop."),
    Q("algorithmic_thinking", "advanced", "php", "Counting nested loop steps",
      """<?php
function pairs(int $n): int {
    $count = 0;
    for ($i = 0; $i < $n; $i++)
        for ($j = $i; $j < $n; $j++)
            $count++;
    return $count;
}
echo pairs(4);""",
      "What does pairs(4) print, what is the general formula, and what is the Big-O?",
      [("prints 10 (4 + 3 + 2 + 1)", ["prints 10", "4 + 3 + 2 + 1", "4+3+2+1", "is 10", "returns 10"], 2),
       ("n(n+1)/2 in general", ["n(n+1)/2", "n(n + 1)/2", "n * (n + 1) / 2"], 1),
       ("which is O(n^2)", ["o(n^2)", "o(n²)", "quadratic"], 1)],
      [],
      "pairs(4) returns 10. The inner loop starts at $j = $i, so it runs 4 + 3 + 2 + 1 times. In general that is "
      "n + (n-1) + … + 1 = n(n+1)/2 steps, about n²/2, which is O(n^2): halving the work does not change the "
      "quadratic growth."),

    # ── C++ ─────────────────────────────────────────────────────────────────
    Q(F, "beginner", "cpp", "Showing the menu with do-while",
      """int shown = 0;
do {
    std::cout << "menu ";
    shown++;
} while (shown < 2);
std::cout << shown;""",
      "What is printed? Why is do-while used for menus?",
      [("prints menu menu 2", ["menu menu 2"], 2),
       ("the condition is checked after the body, so it runs at least once", ["after the body", "at least once", "checked after"], 1),
       ("it stops when shown becomes 2 because 2 < 2 is false", ["2 < 2", "becomes 2", "reaches 2", "is false"], 1)],
      [],
      "It prints menu menu 2. A do-while checks its condition after the body, so the body runs at least once — "
      "exactly what a menu needs (show it, then ask whether to show it again). After the second pass shown becomes "
      "2, 2 < 2 is false, the loop ends and 2 is printed."),
    Q(F, "beginner", "cpp", "Counting down by fours",
      """for (int i = 10; i > 0; i -= 4) {
    std::cout << i << " ";
}""",
      "What is printed? When exactly does the loop stop?",
      [("prints 10 6 2", ["10 6 2"], 2),
       ("i -= 4 subtracts four after each pass", ["subtract", "minus 4", "down by 4", "-= 4"], 1),
       ("next i is -2, and -2 > 0 is false, so it stops", ["-2"], 1)],
      [],
      "It prints 10 6 2. i starts at 10 and i -= 4 subtracts four after each pass: 10, 6, 2. The next value is -2, and "
      "-2 > 0 is false, so the loop stops before printing it."),
    Q("code_tracing", "intermediate", "cpp", "continue in a while loop",
      """int i = 0;
while (i < 5) {
    i++;
    if (i == 3) continue;
    std::cout << i;
}""",
      "What is printed? Why does this continue not cause an infinite loop?",
      [("prints 1245", ["1245"], 2),
       ("continue skips the print for 3 and jumps back to the condition", ["skip", "jumps back", "back to the condition", "next pass", "next iteration"], 1),
       ("i++ happens before the continue, so i still grows", ["before the continue", "still grows", "already incremented", "i++ happens first", "increment first"], 1)],
      [],
      "It prints 1245. Each pass first does i++, then when i == 3 continue skips the print and jumps back to the "
      "condition. Because i++ happens before the continue, i still grows and the loop ends after 5. If the i++ were "
      "after the continue, i would stay 3 forever."),
    Q("debugging", "intermediate", "cpp", "A stray semicolon after for",
      """for (int i = 0; i < 3; i++);
{
    std::cout << "hi ";
}""",
      "The author expected hi hi hi. What is printed, and why?",
      [("prints hi only once", ["once", "one time", "only one"], 2),
       ("the ; right after the for header is an empty loop body", ["empty", "semicolon", "null statement", ";"], 1),
       ("the { } block is a separate statement that runs once after the loop; remove the ;", ["separate", "after the loop", "remove the", "delete the"], 1)],
      [],
      "It prints hi only once. The semicolon right after the for header is an empty statement, so that is the whole "
      "loop body: the loop runs three times doing nothing. The { } block is a separate statement that runs once after "
      "the loop. Remove the ; (and compile with -Wall, which warns about it)."),
    Q("code_tracing", "advanced", "cpp", "break leaves only the inner loop",
      """for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j == 1) break;
        std::cout << i << j << " ";
    }
}""",
      "What is printed? How would you stop both loops instead?",
      [("prints 00 10 20", ["00 10 20"], 2),
       ("break only leaves the inner loop, so the outer loop still runs for every i", ["inner loop", "only the inner", "outer loop still", "every i"], 1),
       ("to stop both: a flag, return from a function, or goto", ["flag", "return", "goto", "function"], 1)],
      [],
      "It prints 00 10 20. For each i the inner loop prints j = 0 and then hits break at j = 1. break only leaves the "
      "inner loop, so the outer loop still runs for every i. C++ has no labelled break: to stop both, set a bool flag "
      "checked by the outer loop, put the loops in a function and return, or (rarely) use goto."),
    Q("debugging", "advanced", "cpp", "A floating-point loop counter",
      """for (double x = 0.0; x != 1.0; x += 0.1) {
    std::cout << x << " ";
}""",
      "This never stops. Why, and how do you write it safely?",
      [("0.1 cannot be stored exactly in binary, so x never equals 1.0 exactly and x != 1.0 stays true", ["exactly", "binary", "rounding", "never equals", "precision"], 2),
       ("never compare floating-point values with == or != as a loop condition", ["==", "!=", "compare"], 1),
       ("fix: count with an int (for int i = 0; i < 10; i++, x = i / 10.0) or use x < 1.0 - 1e-9", ["int", "integer counter", "i < 10", "x < 1"], 1)],
      [],
      "0.1 cannot be stored exactly in binary floating point, so adding it ten times gives 0.9999999999999999 (a tiny "
      "rounding error), which is never exactly 1.0: x != 1.0 stays true and the loop runs forever. Do not use == or != "
      "on floating-point values as a loop condition. Count with an int, for (int i = 0; i < 10; i++) { double x = i / "
      "10.0; … }, or at least use x < 1.0 - 1e-9."),

    # ── General (pseudocode) ────────────────────────────────────────────────
    Q(F, "beginner", "general", "How many times does it run?",
      """count = 0
for i from 1 to 10, step 3:
    count = count + 1
print count""",
      "What is printed? List the values i takes.",
      [("prints 4", ["prints 4", "is 4", "4 times", "four times", "count is 4"], 2),
       ("i takes 1, 4, 7, 10", ["1, 4, 7, 10", "1, 4, 7 and 10", "1 4 7 10"], 1),
       ("the next value 13 is past 10, so the loop stops", ["13"], 1)],
      [],
      "It prints 4. i takes 1, 4, 7 and 10 (10 is included because the loop goes to 10), and count goes up by one for "
      "each. The next value would be 13, which is past 10, so the loop stops: count is 4."),
    Q("algorithms", "intermediate", "general", "Counting a triangle of steps",
      """for i from 1 to n:
    for j from 1 to i:
        do one step""",
      "How many steps run for n = 5? Give the formula for any n and the Big-O.",
      [("15 steps for n = 5 (1 + 2 + 3 + 4 + 5)", ["15", "1 + 2 + 3 + 4 + 5", "1+2+3+4+5"], 2),
       ("n(n+1)/2 in general", ["n(n+1)/2", "n(n + 1)/2", "n * (n + 1) / 2"], 1),
       ("O(n^2), because n(n+1)/2 grows like n²/2", ["o(n^2)", "o(n²)", "quadratic"], 1)],
      [],
      "For n = 5 there are 15 steps: the inner loop runs i times, so 1 + 2 + 3 + 4 + 5. In general that is n(n+1)/2, "
      "which grows like n²/2, so it is O(n^2) — a triangle of work, half a square, still quadratic."),
    Q("logic_problems", "advanced", "general", "Proving a summing loop correct",
      """total = 0
i = 0
while i < n:
    total = total + a[i]
    i = i + 1
# claim: total is the sum of all n elements""",
      "State a loop invariant (true at the top of every pass) and use it to prove the claim.",
      [("invariant: total equals the sum of the first i elements, a[0] .. a[i-1]", ["first i elements", "a[0] .. a[i-1]", "a[0..i-1]"], 2),
       ("it holds at the start: i = 0 and total = 0 is the empty sum", ["empty sum", "at the start", "initially"], 1),
       ("each pass adds a[i] and then increases i, so it stays true", ["stays true", "maintain", "preserv"], 1),
       ("the loop ends with i = n, so total is the sum of all n elements; it ends because i grows towards n", ["i = n", "i == n", "terminat", "ends because"], 1)],
      [],
      "Invariant: at the top of every pass, total equals the sum of the first i elements, a[0] .. a[i-1]. It holds at "
      "the start: i = 0 and total = 0, the empty sum. Each pass adds a[i] and then increases i by 1, so the invariant "
      "stays true (it is maintained). The loop ends because i grows by 1 towards n, and it ends with i = n, so total "
      "is the sum of the first n elements: all of them."),
    # ── Java ────────────────────────────────────────────────────────────────
    Q(F, "beginner", "java", "Enhanced for-each loop over an int[]",
      """int[] nums = {2, 4, 6};
int total = 0;
for (int n : nums) {
    total += n;
}
System.out.println(total);""",
      "What does this print? Walk through each pass of the for-each loop.",
      [("prints 12", ["12", "prints 12"], 2),
       ("n takes the values 2, 4, and 6 in order, adding them into total (0 -> 2 -> 6 -> 12)", ["2, 4, 6", "2, 4, and 6", "0 -> 2", "each element"], 1.5)],
      [],
      "It prints 12. The enhanced `for (int n : nums)` loop visits each element in `nums` in order: `n` is 2 (total "
      "becomes 2), then 4 (total becomes 6), then 6 (total becomes 12)."),

    Q(F, "beginner", "java", "Counting down by twos in Java",
      """for (int i = 6; i > 0; i -= 2) {
    System.out.print(i + " ");
}""",
      "What does this print, and why does the loop stop before printing 0?",
      [("prints 6 4 2", ["6 4 2"], 2),
       ("starts at 6 and subtracts 2 each pass; when i becomes 0 the condition i > 0 is false so the loop stops", ["i > 0", "becomes 0", "subtracts 2", "decreases by 2"], 1.5)],
      [("thinks it prints 6 4 2 0", ["6 4 2 0"], "When i reaches 0, i > 0 is false, so the body does not run for 0.")],
      "It prints 6 4 2. The loop starts at `i = 6` and subtracts 2 after each pass (`6`, `4`, `2`). When `i` becomes "
      "`0`, the condition `i > 0` is false and the loop terminates before printing 0."),

    Q("code_tracing", "intermediate", "java", "continue inside a Java for loop",
      """for (int i = 1; i <= 5; i++) {
    if (i % 2 == 0) {
        continue;
    }
    System.out.print(i + " ");
}""",
      "What does this print, and why doesn't continue cause an infinite loop here?",
      [("prints 1 3 5", ["1 3 5"], 2),
       ("in a for loop, continue jumps to the update step (i++) before re-checking i <= 5, skipping only even numbers", ["i++", "update step", "even", "skips"], 1.5)],
      [],
      "It prints 1 3 5. When `i` is even (`2` and `4`), `continue` skips `System.out.print` and jumps to the `for` "
      "loop's update expression `i++`, so `i` still advances on every iteration and the loop finishes cleanly."),

    Q("debugging", "intermediate", "java", "Off-by-one <= arr.length in a Java loop",
      """int[] arr = {10, 20, 30};
int sum = 0;
for (int i = 0; i <= arr.length; i++) {
    sum += arr[i];
}""",
      "What exception does this loop throw, on which value of i, and how do you fix the loop header?",
      [("throws ArrayIndexOutOfBoundsException when i reaches 3 (arr.length)", ["arrayindexoutofboundsexception", "i == 3", "i reaches 3", "index 3"], 2),
       ("valid indices are 0..arr.length - 1, so fix the condition to i < arr.length", ["i < arr.length", "arr.length - 1"], 1.5)],
      [],
      "It throws `ArrayIndexOutOfBoundsException` when `i` reaches `3` (`arr.length`). A 3-element array has valid "
      "indices `0`, `1`, and `2`; change the condition from `i <= arr.length` to `i < arr.length`."),

    Q("code_tracing", "advanced", "java", "Labeled break outer in nested Java loops",
      """int hits = 0;
outer:
for (int r = 0; r < 3; r++) {
    for (int c = 0; c < 3; c++) {
        if (r == 1 && c == 1) {
            break outer;
        }
        hits++;
    }
}
System.out.println(hits);""",
      "What does this print, and how does break outer differ from an unlabeled break?",
      [("prints 4", ["4", "prints 4"], 2),
       ("counts (0,0), (0,1), (0,2), and (1,0) = 4 hits, then break outer exits both the inner and outer loops immediately (whereas unlabeled break would only exit the inner c loop)", ["both loops", "outer loop", "labeled outer", "inner loop", "(1,0)"], 1.5)],
      [("thinks it prints 7", ["prints 7"], "An unlabeled break would only skip the rest of row 1 and continue with row 2 (7 hits), but break outer terminates the outer loop too.")],
      "It prints 4. Row `r = 0` increments `hits` 3 times (`c = 0, 1, 2`), and row `r = 1` increments `hits` once at "
      "`c = 0` (to 4). At `r = 1, c = 1`, `break outer;` exits the labeled outer `r` loop immediately, whereas a plain "
      "`break;` would only exit the inner `c` loop."),

    Q("debugging", "advanced", "java", "Assigning to the for-each variable does not modify the array",
      """int[] prices = {10, 20, 30};
for (int p : prices) {
    p = p * 2;
}
System.out.println(prices[0] + " " + prices[1]);""",
      "What does this print, why didn't prices change, and how do you double every element in place?",
      [("prints 10 20", ["10 20"], 2),
       ("the for-each variable p is a local copy of each element, so p = p * 2 only modifies p and not the array slot", ["local copy", "copy of each", "does not modify"], 1.5),
       ("fix: use an indexed loop for (int i = 0; i < prices.length; i++) prices[i] *= 2;", ["prices[i]", "indexed"], 1)],
      [("thinks it prints 20 40", ["20 40"], "In Java's enhanced for loop, int p holds a copy of each array element; reassigning p does not write back to prices.")],
      "It prints 10 20. In `for (int p : prices)`, `p` is a local variable that receives a copy of each element; "
      "`p = p * 2` only overwrites that local variable. To mutate the array in place, use an indexed loop: "
      "`for (int i = 0; i < prices.length; i++) prices[i] *= 2;`."),
]
