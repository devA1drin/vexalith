"""Fundamentals: Python — first steps for complete beginners."""

from app.content.qdef import Q

F, P = "fundamentals", "python"

QUESTIONS_FUND_PYTHON = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", P, "Copying a value",
      """x = 5
y = x
x = 10
print(y)""",
      "What does this print? Explain what happens to y when x changes.",
      [("prints 5", ["prints 5", "print 5", "it is 5", "y is 5", "y is still 5", "output is 5", "5 is printed"], 2),
       ("y got the value 5 when it was assigned; changing x later does not change y",
        ["assign", "doesn't change", "does not change", "not change", "unchanged", "copy", "still"], 1)],
      [("thinks y follows x", ["prints 10", "y is 10", "y becomes 10"],
        "y = x copies the current value (5) into y. Giving x a new value later does not update y.")],
      "It prints 5. The line y = x gives y the value x has at that moment, which is 5. Later x = 10 points x at "
      "a new value, but y does not change because they are separate names."),
    Q(F, "beginner", P, "Input is always text",
      """age = input("Age? ")   # the user types 20
print(age + 1)""",
      "The user types 20. What happens, and how do you fix it?",
      [("TypeError: input() returns a string (str), and you cannot add a str and an int",
        ["typeerror", "type error", "returns a string", "is a string", "string", "str"], 2),
       ("fix: convert with int(age)", ["int(", "convert", "cast"], 1)],
      [("thinks it prints 21", ["prints 21", "21"], "input() always gives back text, so \"20\" + 1 fails before any maths happens.")],
      "It crashes with a TypeError. input() always returns a string, so age is the text \"20\", and Python will not "
      "add text and a number. Fix it by converting first: age = int(input(\"Age? \")), then age + 1 is 21."),
    Q(F, "beginner", P, "Three kinds of division",
      """print(7 / 2)
print(7 // 2)
print(7 % 2)""",
      "What are the three lines printed? Explain each operator.",
      [("prints 3.5, 3 and 1 (7 / 2 is 3.5)", ["3.5"], 2),
       ("/ is normal division and always gives a float", ["float", "decimal", "normal division"], 1),
       ("// is floor (whole-number) division and % is the remainder", ["remainder", "floor", "modulo", "whole"], 1)],
      [],
      "It prints 3.5, 3 and 1. / is normal division and always returns a float (3.5). // is floor division: it "
      "drops the decimal part, so 7 // 2 is 3. % gives the remainder: 7 = 2 × 3 + 1, so 7 % 2 is 1."),
    Q(F, "beginner", P, "Strip, upper and length",
      """name = "  Ada Lovelace "
print(name.strip().upper())
print(len(name))""",
      "What are the two lines printed? Did strip() change name?",
      [("first line: ADA LOVELACE in capitals with the outer spaces removed", ["uppercase", "upper case", "capital", "ada lovelace"], 2),
       ("len(name) is 15 because name still has its spaces", ["15"], 1),
       ("strip() returns a new string; the original is unchanged", ["new string", "unchanged", "not changed", "doesn't change", "does not change", "immutable"], 1)],
      [("thinks strip changed name", ["12"], "strip() returns a new string. name itself keeps its spaces, so len(name) is 15.")],
      "The first line is ADA LOVELACE in capitals: strip() removes the spaces at both ends and upper() makes it "
      "uppercase. The second line is 15, because strip() returns a new string and name itself is unchanged: 2 "
      "spaces + 12 letters and space + 1 space = 15."),
    Q(F, "beginner", P, "Grade with elif",
      """score = 75
if score >= 90:
    print("A")
elif score >= 70:
    print("B")
elif score >= 50:
    print("C")
else:
    print("F")""",
      "What is printed? Why not C as well, since 75 >= 50 is also true?",
      [("prints B", ["prints b", "print b", "b is printed", "output is b", "outputs b", "only b", "just b", "'b'", "\"b\""], 2),
       ("an if/elif chain stops at the first true condition, so the rest are skipped",
        ["first true", "first condition", "stops", "skipped", "skip", "only one"], 1)],
      [("thinks several branches run", ["b and c", "b then c", "b, c"], "Only one branch of an if/elif/else chain runs: the first one whose condition is true.")],
      "It prints B. Python checks the conditions from top to bottom: 75 >= 90 is false, 75 >= 70 is true, so it "
      "prints B and stops. The remaining elif and else are skipped, even though 75 >= 50 is also true."),
    Q(F, "beginner", P, "Why four times",
      """for i in range(1, 5):
    print(i)""",
      "Why does this loop run 4 times? Which numbers are printed?",
      [("prints 1 2 3 4", ["1 2 3 4", "1, 2, 3, 4", "1 to 4", "1 through 4", "1-4"], 2),
       ("range stops before the end value: 5 is excluded", ["exclud", "not included", "stops before", "up to but not", "before 5"], 1)],
      [("thinks 5 is printed", ["1 2 3 4 5", "1, 2, 3, 4, 5", "1 to 5", "5 times"], "range(1, 5) starts at 1 and stops before 5.")],
      "It prints 1 2 3 4, so the loop runs 4 times. range(1, 5) starts at 1 and stops before 5: the end value is "
      "excluded. That is why the count is 5 - 1 = 4."),
    Q(F, "beginner", P, "Print is not return",
      """def add(a, b):
    print(a + b)

result = add(2, 3)
print(result)""",
      "What two lines appear? Explain the second one.",
      [("prints 5, then None", ["none"], 2),
       ("the function prints but never returns, so it returns None", ["return"], 1)],
      [("thinks result is 5", ["5 and 5", "5 5", "5 twice", "result is 5"], "print shows a value on screen; only return gives a value back to the caller.")],
      "It prints 5 and then None. Inside add, print(a + b) shows 5 on the screen, but there is no return statement, "
      "so the function gives back None. result is None, and printing it shows None. Use return a + b instead."),
    Q(F, "beginner", P, "Total resets every time",
      """for n in [1, 2, 3]:
    total = 0
    total = total + n
print(total)""",
      "You expected 6 but it prints 3. Find the mistake and fix it.",
      [("total = 0 is inside the loop, so it resets on every iteration",
        ["inside the loop", "every iteration", "each iteration", "reset", "each time", "every time"], 2),
       ("fix: move total = 0 before (outside) the loop", ["before the loop", "outside the loop", "above the loop", "move"], 1)],
      [],
      "total = 0 is indented inside the loop, so it is reset to 0 on every iteration and only the last number (3) "
      "is kept. Fix: move total = 0 before the loop (un-indent it) so the sum builds up to 6."),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", P, "List basics",
      """nums = [3, 1, 2]
nums.append(4)
nums.sort()
print(nums[0], nums[-1], len(nums))""",
      "What is printed? Explain index 0 and index -1.",
      [("prints 1 4 4", ["1 4 4", "1, 4, 4"], 2),
       ("[0] is the first item, [-1] is the last; sort() sorts the list in place",
        ["last", "in place", "first item", "first element"], 1)],
      [],
      "It prints 1 4 4. append adds 4 at the end, sort() sorts the list in place into [1, 2, 3, 4]. nums[0] is the "
      "first item (1), nums[-1] is the last item (4), and len is 4."),
    Q(F, "intermediate", P, "Missing dictionary key",
      """stock = {"apple": 3, "pear": 0}
stock["apple"] += 2
print(stock.get("kiwi", 0), stock["apple"])
print(stock["kiwi"])""",
      "What happens on each print line?",
      [("first line prints 0 5, the last line raises KeyError", ["keyerror", "key error"], 2),
       ("get() returns the default when the key is missing; apple is 3 + 2 = 5", ["0 5", "0, 5", "default"], 1)],
      [],
      "The first line prints 0 5: get(\"kiwi\", 0) returns the default 0 because kiwi is missing, and apple is now "
      "3 + 2 = 5. The last line raises KeyError because square brackets require the key to exist."),
    Q(F, "intermediate", P, "Break and continue",
      """n = 0
while n < 10:
    n += 1
    if n % 2 == 0:
        continue
    if n > 6:
        break
    print(n)""",
      "Which numbers are printed? Explain continue and break.",
      [("prints 1 3 5", ["1 3 5", "1, 3, 5"], 2),
       ("continue skips even numbers; break stops the loop when n reaches 7", ["continue", "break"], 1)],
      [("prints 7 too", ["1 3 5 7", "1, 3, 5, 7"], "When n is 7, the break runs before print, so 7 is never printed.")],
      "It prints 1 3 5. continue jumps back to the top for even numbers, so 2, 4 and 6 are skipped. When n "
      "becomes 7, n > 6 is true and break ends the loop before 7 is printed."),
    Q(F, "intermediate", P, "Counter inside a function",
      """count = 0

def increment():
    count = count + 1

increment()""",
      "This crashes. What is the error and why?",
      [("UnboundLocalError", ["unboundlocalerror", "unbound", "referenced before assignment"], 2),
       ("assigning to count makes it local to the function; fix with return (or global)", ["local", "global", "return"], 1)],
      [],
      "It raises UnboundLocalError. Because the function assigns to count, Python treats count as a local "
      "variable, and the local one has no value yet when count + 1 runs. Better fix: pass the value in and return "
      "it (count = increment(count)); or declare global count."),
    Q(F, "intermediate", P, "And before or",
      """a = True
b = False
c = True
print(a or b and not c)
print(2 + 3 * 4 > 10 and 5 % 2 == 1)""",
      "What are the two lines? Explain the order of operations.",
      [("prints True then True", ["true true", "true, true", "true and true", "both true", "true twice", "true then true", "both lines print true", "both print true", "true and then true"], 2),
       ("precedence: not, then and, then or; * before +", ["precedence", "and before or", "before or", "* before +", "multiplication first", "and binds"], 1)],
      [],
      "Both lines print True. Precedence: not first, then and, then or. not c is False, b and False is False, and "
      "a or False is True. In line 2, * comes before +, so 2 + 12 = 14 > 10 is True, and 5 % 2 == 1 is True."),
    Q(F, "intermediate", P, "Converting types",
      """print(bool("False"))
print(int("42") + 1)
print(int(3.9))
print("3" * 2)""",
      "Predict all four lines. Which one surprises most beginners?",
      [("bool(\"False\") is True: any non-empty string is truthy", ["non-empty", "nonempty", "not empty", "truthy"], 2),
       ("int(\"42\") + 1 is 43", ["43"], 1),
       ("int(3.9) cuts off the decimal: 3 (it does not round)", ["truncat", "cuts off", "drops", "rounds down", "toward zero", "not round", "doesn't round"], 1),
       ("\"3\" * 2 repeats the text: 33", ["33", "repeat"], 1)],
      [],
      "It prints True, 43, 3 and 33. bool(\"False\") is True because any non-empty string is truthy; the words "
      "inside don't matter. int(\"42\") + 1 is 43. int(3.9) cuts off the decimal part (it does not round) giving 3. "
      "\"3\" * 2 repeats the text, giving 33."),
    Q(F, "intermediate", P, "Finally always runs",
      """def safe_div(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("cannot divide by zero")
        return None
    finally:
        print("done")

print(safe_div(6, 3))
print(safe_div(1, 0))""",
      "Write out every line printed, in order.",
      [("finally always runs, even after return, so done prints before each result", ["finally", "always run"], 2),
       ("first call: done then 2.0", ["2.0"], 1),
       ("second call: the message, done, then None", ["none"], 1)],
      [],
      "Output: done, 2.0, cannot divide by zero, done, None. The finally block always runs, even when the try "
      "returns, so done is printed before the caller prints the result. 6 / 3 is 2.0 (a float). Dividing by zero "
      "jumps to except, which prints the message and returns None."),
    Q(F, "intermediate", P, "Two names, one list",
      """a = [1, 2]
b = a
b.append(3)
print(a)""",
      "What is printed? Why did a change when we only touched b?",
      [("prints [1, 2, 3]", ["[1, 2, 3]"], 2),
       ("b = a does not copy; both names refer to the same list", ["same list", "same object", "not a copy", "doesn't copy", "does not copy", "reference"], 1)],
      [("thinks a is unchanged", ["[1, 2]"], "b = a does not copy the list; a and b are two names for one list.")],
      "It prints [1, 2, 3]. b = a does not copy the list: a and b are two names for the same list object, so "
      "appending through b is visible through a. Use b = a.copy() (or list(a)) for a separate list."),
    Q(F, "intermediate", P, "Match a status code",
      """def describe(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case _:
            return "Other"

print(describe(404), describe(500))""",
      "What is printed? What does case _ do?",
      [("prints Not Found Other", ["not found other", "not found, other", "not found and other"], 2),
       ("case _ is the wildcard/default branch that matches anything else", ["wildcard", "default", "anything else", "everything else"], 1)],
      [],
      "It prints Not Found Other. 404 matches the second case. 500 matches no number, so it falls to case _, the "
      "wildcard (default) branch that matches anything else."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", P, "Shopping cart default",
      """def add_item(item, cart=[]):
    cart.append(item)
    return cart

print(add_item("pen"))
print(add_item("ink"))""",
      "The second call prints something unexpected. What, and why? Fix it.",
      [("second call prints ['pen', 'ink']", ["'pen', 'ink'", "pen, ink", "pen and ink", "[\"pen\", \"ink\"]"], 2),
       ("the default list is created once, when the function is defined, and shared by all calls", ["once", "shared", "defined", "same list"], 1),
       ("fix: default to None and create a new list inside", ["none"], 1)],
      [],
      "The second call prints ['pen', 'ink']. The default list is created once, when the function is defined, so "
      "every call that omits cart shares the same list. Fix: def add_item(item, cart=None): and inside, if cart is "
      "None: cart = []."),
    Q(F, "advanced", P, "Found at index zero",
      """def find(names, target):
    for i, n in enumerate(names):
        if n == target:
            return i

idx = find(["ann", "bo"], "ann")
if idx:
    print("found at", idx)
else:
    print("not found")""",
      "ann is in the list, yet what does this print? Fix the check.",
      [("prints not found", ["not found"], 2),
       ("idx is 0, and 0 is falsy", ["falsy", "0 is false", "zero"], 1),
       ("fix: if idx is not None", ["is not none", "is none"], 1)],
      [("thinks it prints found at 0", ["found at 0"], "0 counts as false in an if, so the else branch runs.")],
      "It prints not found. ann is at index 0, and 0 is falsy, so if idx: takes the else branch. The function "
      "returns None when nothing matches, so test that explicitly: if idx is not None:."),
    Q(F, "advanced", P, "Equal but not identical",
      """a = [1, 2]
b = [1, 2]
c = a
print(a == b, a is b, a is c)""",
      "What is printed? Explain == versus is.",
      [("prints True False True", ["true false true", "true, false, true"], 2),
       ("== compares values; is checks identity (the same object)", ["identity", "same object", "values"], 1)],
      [],
      "It prints True False True. == compares values, and both lists contain 1 and 2. is checks identity, i.e. "
      "whether both names point to the same object: a and b are two separate lists, while c is the same object as a."),
    Q(F, "advanced", P, "Point one plus point two",
      """print(0.1 + 0.2 == 0.3)
print(round(0.1 + 0.2, 2) == 0.3)""",
      "What are the two results, and why?",
      [("False, then True", ["false true", "false, true", "false and true", "false then true", "false and then true", "false, then true"], 2),
       ("floats are stored in binary and cannot represent 0.1 exactly; compare with rounding or math.isclose",
        ["binary", "floating", "isclose", "approximat", "exactly"], 1)],
      [],
      "It prints False and then True. Floats are stored in binary, which cannot represent 0.1 or 0.2 exactly, so "
      "the sum is 0.30000000000000004. Rounding (or math.isclose) compares the values safely."),
    Q(F, "advanced", P, "One step too far",
      """items = ["a", "b", "c"]
i = 0
while i <= len(items):
    print(items[i])
    i += 1""",
      "It prints a, b, c and then crashes. What error, and what is the fix?",
      [("IndexError when i reaches 3", ["indexerror", "index error", "out of range"], 2),
       ("valid indexes are 0..2; the condition must be i < len(items) (or use for item in items)", ["< len", "for item in"], 1)],
      [],
      "After printing c, i becomes 3 and 3 <= 3 is still true, so items[3] raises IndexError: list index out of "
      "range. Valid indexes are 0 to 2. Use while i < len(items), or simply for item in items."),
    Q(F, "advanced", P, "Hours and minutes",
      """minutes = 135
print(minutes // 60, "h", minutes % 60, "min")
print("Total: " + minutes)""",
      "What does the first line print? What goes wrong on the second?",
      [("second line: TypeError, cannot concatenate str and int", ["typeerror", "type error"], 2),
       ("first line prints 2 h 15 min", ["2 h 15 min", "2 h 15", "2h 15"], 1),
       ("fix with str(minutes) or an f-string", ["str(", "f-string", "fstring", "f\"", "format"], 1)],
      [],
      "The first line prints 2 h 15 min: 135 // 60 is 2 whole hours and 135 % 60 is 15 minutes left over. The "
      "second line raises TypeError because + cannot join a str and an int. Use \"Total: \" + str(minutes) or "
      "f\"Total: {minutes}\"."),
    Q(F, "advanced", P, "Counting words",
      """words = ["a", "b", "a", "c", "a"]
counts = {}
for w in words:
    if w in counts:
        counts[w] += 1
    else:
        counts[w] = 1
print(counts)""",
      "What is printed? Walk through the first two iterations.",
      [("prints {'a': 3, 'b': 1, 'c': 1}", ["'a': 3", "a: 3", "a is 3", "a 3 times", "a appears 3"], 2),
       ("a new word starts at 1 (else branch); a word seen before adds 1", ["first time", "start", "else", "new"], 1)],
      [],
      "It prints {'a': 3, 'b': 1, 'c': 1}. The first time a word is seen it is not in counts, so the else branch "
      "starts it at 1; every later time the if branch adds 1. a appears 3 times."),
    Q(F, "advanced", P, "Min and max of nothing",
      """def stats(xs):
    return min(xs), max(xs)

low, high = stats([4, 9, 1])
print(low, high)
print(stats([]))""",
      "What does the first print show? What happens on the last line?",
      [("the last line raises ValueError: min() of an empty list", ["valueerror", "value error"], 2),
       ("first print shows 1 9", ["1 9", "1, 9", "1 and 9"], 1),
       ("return a, b returns a tuple that is unpacked into low, high", ["tuple", "unpack"], 1)],
      [],
      "The first print shows 1 9: return min(xs), max(xs) returns a tuple, which is unpacked into low and high. "
      "The last line raises ValueError because min() of an empty list has no answer; check for an empty list first."),
]
