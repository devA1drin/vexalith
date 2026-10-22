"""Fundamentals: JavaScript — first steps for complete beginners."""

from app.content.qdef import Q

F, J = "fundamentals", "javascript"

QUESTIONS_FUND_JAVASCRIPT = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", J, "let versus const",
      """const name = "Ada";
let age = 36;
age = age + 1;
name = "Grace";
console.log(name, age);""",
      "What happens when this runs? Explain let and const.",
      [("TypeError: assignment to a constant variable", ["typeerror", "type error", "assignment to constant", "assignment to a constant", "cannot reassign", "can't reassign"], 2),
       ("let can be reassigned, const cannot; the program stops so nothing is logged", ["nothing", "never", "not logged", "stops"], 1)],
      [("thinks it logs Grace 37", ["grace 37"], "const variables cannot be given a new value; the program stops with an error first.")],
      "It throws TypeError: Assignment to constant variable on the line name = \"Grace\". let variables (age) can "
      "be reassigned, const variables cannot. The error stops the program, so nothing is logged."),
    Q(F, "beginner", J, "Double or triple equals",
      """console.log(1 == "1");
console.log(1 === "1");
console.log(0 == false);""",
      "What are the three results? When should you use ===?",
      [("true, false, true", ["true false true", "true, false, true"], 2),
       ("== converts types before comparing; === requires the same type and value", ["convert", "coerc", "same type"], 1)],
      [],
      "It logs true, false, true. == converts both sides to a common type before comparing, so \"1\" becomes 1 "
      "and false becomes 0. === also requires the same type, so 1 === \"1\" is false. Prefer === to avoid surprises."),
    Q(F, "beginner", J, "Plus joins, minus subtracts",
      """console.log("5" + 3);
console.log("5" - 3);
console.log(5 + 3 + "px");""",
      "Predict the three lines and explain the difference.",
      [("53, 2, 8px", ["53 2 8px", "53, 2, 8px", "53, 2 and 8px", "53, 2, and 8px"], 2),
       ("+ with a string joins (concatenates); - always converts to numbers; evaluated left to right",
        ["concaten", "join", "left to right"], 1)],
      [],
      "It logs 53, 2 and 8px. + with a string concatenates (joins text), so \"5\" + 3 is \"53\". - only works on "
      "numbers, so \"5\" is converted and 5 - 3 is 2. The last line runs left to right: 5 + 3 = 8 first, then "
      "8 + \"px\" joins to \"8px\"."),
    Q(F, "beginner", J, "Switch without break",
      """const day = 2;
switch (day) {
  case 1: console.log("Mon");
  case 2: console.log("Tue");
  case 3: console.log("Wed");
    break;
  default: console.log("?");
}""",
      "What is logged? Why?",
      [("Tue then Wed", ["tue wed", "tue, wed", "tue and wed", "tue then wed", "tue and then wed", "tue, then wed"], 2),
       ("without break, execution falls through into the next case", ["fall", "break"], 1)],
      [("thinks only Tue", ["only tue", "just tue"], "A case without break keeps running into the next case.")],
      "It logs Tue and then Wed. switch jumps to case 2 and logs Tue, but there is no break, so it falls through "
      "into case 3 and logs Wed; the break there stops it before default."),
    Q(F, "beginner", J, "Loop runs one extra time",
      """const fruits = ["apple", "pear", "fig"];
for (let i = 0; i <= fruits.length; i++) {
  console.log(fruits[i]);
}""",
      "What is logged on the last line, and what is the mistake?",
      [("the last line is undefined", ["undefined"], 2),
       ("i <= length goes one past the end; use i < fruits.length", ["< fruits.length", "one past", "off-by-one", "off by one", "one extra"], 1)],
      [],
      "It logs apple, pear, fig and then undefined. Indexes go from 0 to 2, but i <= fruits.length lets i reach 3 "
      "— one past the end (an off-by-one error). Use i < fruits.length."),
    Q(F, "beginner", J, "Forgot to return",
      """function double(n) {
  n * 2;
}
console.log(double(4));""",
      "Why doesn't this log 8?",
      [("it logs undefined", ["undefined"], 2),
       ("the function has no return statement", ["return"], 1)],
      [],
      "It logs undefined. n * 2 is calculated and then thrown away because there is no return statement, and a "
      "function without return gives back undefined. Write return n * 2;."),
    Q(F, "beginner", J, "Array basics",
      """const nums = [10, 20, 30];
nums.push(40);
console.log(nums.length, nums[0], nums[nums.length - 1]);""",
      "What is logged? Why is push allowed on a const array?",
      [("logs 4 10 40", ["4 10 40", "4, 10, 40"], 2),
       ("push adds to the end; const stops reassignment, not changing the contents", ["reassign", "contents", "mutat", "change the array"], 1)],
      [],
      "It logs 4 10 40. push adds 40 at the end, so the length is 4; index 0 is the first item and length - 1 is "
      "the last. const only stops you from reassigning nums to a new array; changing its contents is allowed."),
    Q(F, "beginner", J, "Nothing and null",
      """let a;
const b = null;
console.log(a, b, typeof a, typeof b);""",
      "What is logged? Which result is a famous JavaScript quirk?",
      [("typeof null is \"object\"", ["object"], 2),
       ("a was declared without a value, so it is undefined", ["undefined"], 1)],
      [],
      "It logs undefined null \"undefined\" \"object\". a was declared but never given a value, so it is undefined. "
      "null means 'deliberately empty'. typeof null being \"object\" is a historical bug kept for compatibility."),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", J, "var leaks out of blocks",
      """if (true) {
  var x = 1;
  let y = 2;
}
console.log(x);
console.log(y);""",
      "What happens on each console.log?",
      [("logs 1, then ReferenceError for y", ["referenceerror", "reference error", "not defined"], 2),
       ("var ignores block scope (function-scoped); let is block-scoped", ["block", "function-scoped", "function scoped", "function scope"], 1)],
      [],
      "The first line logs 1, the second throws ReferenceError: y is not defined. var is function-scoped, so x "
      "escapes the if block. let is block-scoped: y only exists inside the braces."),
    Q(F, "intermediate", J, "Object properties",
      """const user = { name: "Lin", "favorite color": "green" };
user.age = 30;
console.log(user.name, user["favorite color"], user.email);
console.log(Object.keys(user).length);""",
      "Predict both lines. When do you need square brackets?",
      [("logs Lin green undefined", ["lin green undefined", "lin, green, undefined"], 2),
       ("a missing property is undefined (no error); after adding age there are 3 keys", ["3"], 1),
       ("brackets are needed for keys with spaces (or keys in variables)", ["space", "bracket"], 1)],
      [],
      "It logs Lin green undefined, then 3. A missing property like email is just undefined, not an error. After "
      "user.age = 30 there are 3 keys. Square brackets are needed for keys with spaces or keys stored in variables."),
    Q(F, "intermediate", J, "Default with or versus ??",
      """const input = "";
const name = input || "Guest";
const count = 0;
const shown = count ?? 10;
console.log(name, shown);""",
      "What is logged? How do || and ?? differ?",
      [("logs Guest 0", ["guest 0", "guest, 0", "guest and 0"], 2),
       ("|| falls back on any falsy value; ?? only on null or undefined", ["falsy", "null", "undefined"], 1)],
      [],
      "It logs Guest 0. || uses the right side for any falsy value, and the empty string is falsy, so name is "
      "Guest. ?? only falls back for null or undefined; 0 is neither, so shown stays 0."),
    Q(F, "intermediate", J, "Order of operations",
      """console.log(2 + 3 * 4);
console.log((2 + 3) * 4);
console.log(10 / 4, 10 % 4, Math.floor(10 / 4));""",
      "Predict each line.",
      [("14: multiplication happens before addition", ["14"], 1),
       ("20 with the parentheses", ["20"], 1),
       ("2.5 2 2: / never does integer division, % is the remainder, floor rounds down", ["2.5"], 1)],
      [],
      "It logs 14, then 20, then 2.5 2 2. * runs before +, so 2 + 12 = 14; parentheses force (5) * 4 = 20. In "
      "JavaScript 10 / 4 is 2.5 (no integer division), 10 % 4 is the remainder 2, and Math.floor rounds 2.5 down to 2."),
    Q(F, "intermediate", J, "String methods",
      """const s = "JavaScript";
console.log(s.length, s[0], s.slice(0, 4), s.toUpperCase(), s.indexOf("Script"));""",
      "What is logged? Explain slice's end index.",
      [("10 J Java JAVASCRIPT 4", ["10 j java javascript 4", "10, j, java, javascript, 4"], 2),
       ("indexes start at 0 and slice's end index is excluded", ["exclud", "start at 0", "zero", "0-based", "not included"], 1)],
      [],
      "It logs 10 J Java JAVASCRIPT 4. Indexes start at 0, so s[0] is J. slice(0, 4) takes indexes 0 to 3 — the "
      "end index is excluded — giving Java. \"Script\" starts at index 4."),
    Q(F, "intermediate", J, "Number versus parseInt",
      """console.log(Number("42px"), parseInt("42px"), Number(""), Boolean("0"));""",
      "Predict all four values.",
      [("NaN 42 0 true", ["nan 42 0 true", "nan, 42, 0, true"], 2),
       ("Number needs the whole string to be numeric; parseInt reads leading digits; a non-empty string is truthy",
        ["leading", "whole", "non-empty", "truthy", "start"], 1)],
      [],
      "It logs NaN 42 0 true. Number() needs the whole string to be a number, so \"42px\" is NaN. parseInt reads "
      "the leading digits and stops at p, giving 42. An empty string converts to 0. \"0\" is a non-empty string, "
      "so it is truthy."),
    Q(F, "intermediate", J, "Catching bad JSON",
      """function parse(text) {
  try {
    return JSON.parse(text);
  } catch (err) {
    console.log("bad input");
    return null;
  }
}
console.log(parse('{"a": 1}').a);
console.log(parse("{a: 1}"));""",
      "What is logged, line by line?",
      [("1, then bad input, then null", ["bad input"], 2),
       ("the second text is invalid JSON (keys need double quotes), so JSON.parse throws and catch runs",
        ["double quote", "quotes", "invalid", "syntaxerror"], 1)],
      [],
      "It logs 1, then bad input, then null. The first text is valid JSON, so .a is 1. In the second, the key a has "
      "no double quotes, so it is invalid JSON: JSON.parse throws, catch logs bad input and returns null."),
    Q(F, "intermediate", J, "Skip three, stop after five",
      """let i = 0;
while (true) {
  i++;
  if (i === 3) continue;
  if (i > 5) break;
  console.log(i);
}""",
      "Which numbers are logged, and why does the loop end?",
      [("logs 1 2 4 5", ["1 2 4 5", "1, 2, 4, 5"], 2),
       ("continue skips 3; break ends the loop when i is 6", ["continue", "break"], 1)],
      [],
      "It logs 1 2 4 5. continue jumps back to the top when i is 3, so 3 is skipped. When i becomes 6, i > 5 is "
      "true and break ends the otherwise endless while (true) loop."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", J, "Used before declared",
      """console.log(a);
var a = 5;
console.log(b);
let b = 6;""",
      "What happens on each console.log?",
      [("undefined, then ReferenceError (cannot access b before initialization)",
        ["referenceerror", "reference error", "before initialization", "temporal dead zone", "tdz"], 2),
       ("var declarations are hoisted (without the value); let is in the temporal dead zone", ["hoist"], 1)],
      [("thinks the first line logs 5", ["logs 5", "prints 5"], "Only the declaration of var is hoisted, not the value 5.")],
      "The first line logs undefined, the second throws ReferenceError: Cannot access 'b' before initialization. "
      "var declarations are hoisted to the top without their value. let is also hoisted but sits in the temporal "
      "dead zone until its line runs."),
    Q(F, "advanced", J, "Objects are shared",
      """const a = { score: 1 };
const b = a;
b.score = 99;
const c = { ...a };
c.score = 5;
console.log(a.score, b.score, c.score);""",
      "Predict the output and explain each variable.",
      [("99 99 5", ["99 99 5", "99, 99, 5"], 2),
       ("b refers to the same object as a; the spread makes a (shallow) copy", ["same object", "reference", "copy", "spread"], 1)],
      [],
      "It logs 99 99 5. b = a does not copy: both names refer to the same object, so setting b.score changes "
      "a.score too. { ...a } spreads the properties into a new (shallow) copy, so changing c leaves a alone."),
    Q(F, "advanced", J, "Comparing arrays",
      """console.log([1, 2] === [1, 2]);
console.log([] == false);
console.log([1, 2, 3].includes(2));""",
      "Predict the three results.",
      [("false true true", ["false true true", "false, true, true"], 2),
       ("=== on arrays compares references, not contents; [] == false converts both to 0", ["reference", "coerc", "convert"], 1)],
      [],
      "It logs false, true, true. === on arrays compares references: two separate arrays are never the same object. "
      "[] == false converts both sides to numbers ([] → \"\" → 0, false → 0), so it is true. includes checks the "
      "contents, and 2 is there."),
    Q(F, "advanced", J, "Defaults only for undefined",
      """function greet(name = "friend", greeting) {
  return `${greeting}, ${name}!`;
}
console.log(greet());
console.log(greet(undefined, "Hi"));
console.log(greet(null, "Yo"));""",
      "Predict all three lines.",
      [("the last line is Yo, null! — defaults do not replace null", ["yo, null"], 2),
       ("defaults apply only when the argument is undefined", ["only when", "only for undefined", "only if"], 1),
       ("first line: undefined, friend! (greeting has no default)", ["undefined, friend"], 1)],
      [],
      "It logs \"undefined, friend!\", \"Hi, friend!\" and \"Yo, null!\". Default values apply only when the argument "
      "is undefined (missing or passed as undefined). null is a real value, so it is used. greeting has no default, "
      "so it is undefined in the first call."),
    Q(F, "advanced", J, "toFixed returns text",
      """console.log(0.1 + 0.2 === 0.3);
console.log((0.1 + 0.2).toFixed(2));
console.log(typeof (0.1 + 0.2).toFixed(2));""",
      "Predict the three lines and explain the first.",
      [("false, then 0.30", ["0.30"], 2),
       ("floating point is binary and cannot store 0.1 exactly", ["binary", "floating", "precision", "exactly"], 1),
       ("toFixed returns a string", ["string"], 1)],
      [],
      "It logs false, \"0.30\" and \"string\". Numbers are binary floating point and cannot store 0.1 or 0.2 exactly, "
      "so the sum is 0.30000000000000004. toFixed(2) rounds for display and returns a string, not a number."),
    Q(F, "advanced", J, "Counting down by three",
      """for (let i = 10; i > 0; i -= 3) {
  console.log(i);
}""",
      "How many times does the loop run? Show the values and why it stops.",
      [("runs 4 times: 10, 7, 4, 1", ["10 7 4 1", "10, 7, 4, 1", "4 times", "four times"], 2),
       ("after 1, i becomes -2 and i > 0 is false", ["-2"], 1)],
      [],
      "It runs 4 times and logs 10, 7, 4, 1. After logging 1, i -= 3 makes i equal -2, so i > 0 is false and the "
      "loop stops."),
    Q(F, "advanced", J, "Checking for NaN",
      """const price = Number("abc");
console.log(price === NaN);
console.log(Number.isNaN(price));
console.log(typeof price);""",
      "Predict the three lines. How should you test for NaN?",
      [("false true number", ["false true number", "false, true, number"], 2),
       ("NaN is not equal to anything, even itself; use Number.isNaN", ["itself", "isnan"], 1)],
      [],
      "It logs false, true, number. NaN is the only value not equal to itself, so price === NaN is always false. "
      "Use Number.isNaN(price). NaN ('not a number') is still of type number."),
    Q(F, "advanced", J, "Braces in an arrow function",
      """const nums = [1, 2, 3, 4];
const out = nums
  .filter(n => n % 2 === 0)
  .map(n => { n * 10 });
console.log(out);""",
      "Expected [20, 40]. What is logged, and why?",
      [("[undefined, undefined]", ["undefined"], 2),
       ("braces make a block body that needs return; write n => n * 10", ["return", "braces", "block"], 1)],
      [],
      "It logs [undefined, undefined]. filter keeps 2 and 4, but in map the braces make a block body, and a block "
      "needs an explicit return. Without it each call returns undefined. Write n => n * 10 or n => { return n * 10; }."),
]
