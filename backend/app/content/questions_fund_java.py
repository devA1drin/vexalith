"""Fundamentals questions for Java (8 beginner, 8 intermediate, 8 advanced)."""

from app.content.qdef import Q

F, J = "fundamentals", "java"

QUESTIONS_FUND_JAVA = [
    # ── Beginner (8) ────────────────────────────────────────────────────────
    Q(F, "beginner", J, "System.out.print vs System.out.println",
      """System.out.print("A");
System.out.println("B");
System.out.print("C");""",
      "What does this print, and why are A and B on the same line while C is on the next line?",
      [("prints AB on the first line and C on the second line", ["ab", "second line", "next line"], 2),
       ("print does not add a newline at the end, whereas println adds a newline after printing", ["newline", "print(", "println("], 1.5)],
      [("thinks each call prints on its own line", ["three lines", "a then b then c on separate"], "System.out.print stays on the same line; only println ends the line.")],
      "It prints AB on the first line and C on the second line. System.out.print(\"A\") outputs A without a newline, "
      "so System.out.println(\"B\") prints B right after A and then adds a newline, placing C on the next line."),

    Q(F, "beginner", J, "Copying an int variable in Java",
      """int x = 5;
int y = x;
x = 12;
System.out.println(y);""",
      "What does this print, and why doesn't changing x to 12 change y?",
      [("prints 5", ["5", "prints 5"], 2),
       ("int is a primitive value type, so y = x copies the value 5 into y independently", ["copy", "copies", "primitive", "own value", "independent"], 1.5)],
      [("thinks it prints 12 because y is linked to x", ["prints 12", "12"], "Primitive assignments copy the number at that moment; y does not track later changes to x.")],
      "It prints 5. When int y = x runs, Java copies the primitive value 5 into y. Reassigning x = 12 later only "
      "updates x; y keeps its own copy of 5."),

    Q(F, "beginner", J, "Integer division and remainder in Java",
      """System.out.println(7 / 2);
System.out.println(7 % 2);
System.out.println(7.0 / 2);""",
      "What do the three lines print, and why does 7 / 2 give a different result from 7.0 / 2?",
      [("prints 3, then 1, then 3.5", ["3", "1", "3.5"], 2),
       ("7 / 2 divides two ints (integer division) and truncates the fraction, while 7.0 is a double so 7.0 / 2 performs floating-point division", ["integer division", "truncat", "double", "decimal", "thrown away"], 1.5),
       ("7 % 2 is the remainder after dividing 7 by 2", ["remainder", "modulo"], 0.5)],
      [("thinks 7 / 2 prints 3.5", ["7 / 2 is 3.5"], "When both operands are int, Java performs integer division and drops the .5.")],
      "It prints 3, then 1, then 3.5. Because 7 and 2 are both ints, 7 / 2 is integer division and drops the decimal "
      "part to give 3. 7 % 2 gives the remainder 1. Because 7.0 is a double, 7.0 / 2 keeps the decimal and prints 3.5."),

    Q(F, "beginner", J, "String concatenation vs addition order",
      """System.out.println("Score: " + 3 + 4);
System.out.println("Score: " + (3 + 4));""",
      "What do the two lines print, and why are they different?",
      [("first prints Score: 34 and second prints Score: 7", ["score: 34", "score: 7"], 2),
       ("+ evaluates left to right: \"Score: \" + 3 produces the String \"Score: 3\", then + 4 concatenates \"4\", whereas parentheses compute 3 + 4 = 7 first", ["left to right", "concaten", "parentheses", "score: 3"], 1.5)],
      [("thinks both print Score: 7", ["both print score: 7"], "Without parentheses, + associates left to right starting with a String, so both + operators concatenate text.")],
      "The first line prints Score: 34 and the second prints Score: 7. The + operator runs left to right: "
      "\"Score: \" + 3 concatenates to the String \"Score: 3\", and adding 4 concatenates again to \"Score: 34\". "
      "In the second line, parentheses force integer addition (3 + 4 = 7) before concatenating."),

    Q(F, "beginner", J, "Combining conditions with && and ||",
      """int age = 20;
boolean hasTicket = false;
boolean isVip = true;
System.out.println(age >= 18 && hasTicket);
System.out.println(hasTicket || isVip);""",
      "What do the two lines print, and why?",
      [("prints false then true", ["false", "true"], 2),
       ("&& requires both sides to be true (hasTicket is false), while || is true when at least one side is true (isVip is true)", ["both", "at least one", "&&", "||"], 1.5)],
      [],
      "It prints false then true. The && (and) operator is true only when both sides are true—hasTicket is false, so "
      "the first line is false. The || (or) operator is true when at least one side is true, and isVip is true."),

    Q(F, "beginner", J, "First and last element of a Java array",
      """int[] scores = {10, 20, 30, 40};
System.out.println(scores[0] + scores[scores.length - 1]);""",
      "What does this print, and why is the last index scores.length - 1 instead of scores.length?",
      [("prints 50 (10 + 40)", ["50", "prints 50"], 2),
       ("Java arrays are 0-indexed, so a 4-element array has indices 0, 1, 2, 3 and scores.length - 1 is index 3", ["0-index", "zero-index", "starts at 0", "0, 1, 2, 3", "index 3"], 1.5)],
      [("thinks scores[0] is 20", ["scores[0] is 20"], "Array indexing in Java starts at 0, so scores[0] is 10.")],
      "It prints 50. Java arrays start at index 0, so scores[0] is 10 and the four elements sit at indices 0, 1, 2, "
      "and 3. Because scores.length is 4, the last element is at scores.length - 1 (index 3, which is 40), and "
      "10 + 40 = 50."),

    Q(F, "beginner", J, "if / else if / else first matching branch",
      """int mark = 85;
if (mark >= 90) {
    System.out.println("A");
} else if (mark >= 80) {
    System.out.println("B");
} else if (mark >= 70) {
    System.out.println("C");
}""",
      "What does this print, and why doesn't it also print C even though 85 >= 70 is true?",
      [("prints B", ["prints b", "\"b\"", "only b"], 2),
       ("in an if / else if chain Java runs only the first branch whose condition is true and skips the rest", ["first", "skips the rest", "only one branch", "else if"], 1.5)],
      [("thinks it prints B and C", ["b and c"], "else if branches are only checked when all earlier conditions in the chain were false.")],
      "It prints B. Java checks the conditions top to bottom: 85 >= 90 is false, 85 >= 80 is true, so it prints B "
      "and skips every remaining else if branch in the chain."),

    Q(F, "beginner", J, "Calling a static helper method",
      """public class MathDemo {
    static int doubleIt(int n) {
        return n * 2;
    }
    public static void main(String[] args) {
        int result = doubleIt(6) + 3;
        System.out.println(result);
    }
}""",
      "What does main print, and what happens step by step when doubleIt(6) is called?",
      [("prints 15", ["15", "prints 15"], 2),
       ("doubleIt(6) receives n = 6, returns 12, and main adds 3 to get 15", ["returns 12", "12 + 3", "n = 6"], 1.5)],
      [],
      "It prints 15. Calling doubleIt(6) passes 6 as parameter n and returns 6 * 2 = 12. Back in main, 12 + 3 is 15, "
      "which is stored in result and printed."),

    # ── Intermediate (8) ────────────────────────────────────────────────────
    Q(F, "intermediate", J, "Comparing Strings: == vs .equals()",
      """String a = new String("hello");
String b = new String("hello");
System.out.println(a == b);
System.out.println(a.equals(b));""",
      "What do the two lines print, and why do == and .equals() give different answers here?",
      [("prints false then true", ["false", "true"], 2),
       ("== on reference types checks whether a and b point to the exact same object in memory, whereas .equals() compares the characters inside the Strings", ["same object", "reference", "memory", "equals", "characters", "content"], 1.5)],
      [("thinks both print true because the text is identical", ["both print true"], "In Java, == on Strings checks object identity (reference equality), not text content.")],
      "It prints false then true. Each `new String(\"hello\")` allocates a distinct String object in memory; `a == b` "
      "checks whether `a` and `b` refer to the same object (false), while `a.equals(b)` compares their character "
      "sequences (true)."),

    Q(F, "intermediate", J, "Primitive int vs int[] array passed to a method",
      """static void tweak(int n, int[] arr) {
    n = 99;
    arr[0] = 99;
}
public static void main(String[] args) {
    int x = 1;
    int[] nums = {1, 2};
    tweak(x, nums);
    System.out.println(x + " " + nums[0]);
}""",
      "What does main print, and why did nums[0] change while x stayed the same?",
      [("prints 1 99", ["1 99", "1 and 99"], 2),
       ("x is passed as a copy of the primitive int 1 so n = 99 only changes the local parameter, while arr receives a copy of the reference pointing to the same array object so arr[0] = 99 mutates it", ["primitive", "copy", "reference", "same array", "mutat"], 1.5)],
      [],
      "It prints 1 99. Java passes arguments by value: `n` gets a copy of the primitive int `1`, so `n = 99` only "
      "modifies the local parameter. `arr` gets a copy of the reference to `nums`, so both `arr` and `nums` point to "
      "the same array in memory and `arr[0] = 99` mutates element 0."),

    Q(F, "intermediate", J, "ArrayList add, set, and size",
      """import java.util.ArrayList;

ArrayList<Integer> list = new ArrayList<>();
list.add(10);
list.add(20);
list.set(0, 50);
System.out.println(list + " size=" + list.size());""",
      "What does this print, and what is the difference between list.add(...) and list.set(0, 50)?",
      [("prints [50, 20] size=2", ["[50, 20]", "size=2"], 2),
       ("add appends a new element and grows the list, whereas set(0, 50) replaces the existing element at index 0 without changing size()", ["replace", "append", "index 0", "without changing"], 1.5)],
      [("thinks set inserts a third element (size=3)", ["size=3", "[50, 10, 20]"], "list.set(index, value) overwrites the element at that index; list.add(index, value) inserts.")],
      "It prints [50, 20] size=2. `add(10)` and `add(20)` append two elements, then `set(0, 50)` overwrites the "
      "element at index 0 in place without adding a new slot, so the size remains 2."),

    Q(F, "intermediate", J, "NullPointerException when calling a method on null",
      """String name = null;
if (name != null && name.isEmpty()) {
    System.out.println("empty");
}
System.out.println(name.length());""",
      "Why does the if statement succeed without crashing, while the last line throws an exception?",
      [("the if uses short-circuit && so name.isEmpty() is skipped when name != null is false, but name.length() dereferences null and throws NullPointerException", ["nullpointerexception", "short-circuit", "skipped", "null"], 2),
       ("fix: check name != null before calling name.length()", ["name != null", "guard"], 1)],
      [],
      "In the if condition, `name != null` is false, so short-circuit `&&` skips `name.isEmpty()`. On the next line, "
      "calling `name.length()` directly on `null` throws a `NullPointerException`. Guard it with `if (name != null)` "
      "first."),

    Q(F, "intermediate", J, "final on an array reference vs array elements",
      """final int[] nums = {1, 2, 3};
nums[0] = 99;
System.out.println(nums[0]);""",
      "Does this code compile and what does it print? What does final on nums actually prevent?",
      [("compiles and prints 99", ["99", "prints 99", "compiles"], 2),
       ("final on a reference variable prevents reassigning nums to a different array (nums = ...), but does not make the array contents immutable", ["reassign", "reference", "contents", "elements", "mutable"], 1.5)],
      [("thinks final makes nums[0] = 99 a compile error", ["compile error", "does not compile"], "final locks the reference binding nums, not the elements stored inside the array.")],
      "It compiles and prints 99. Marking `nums` as `final` means the variable `nums` cannot be reassigned to point "
      "to a different array (`nums = new int[]{4, 5}` would fail to compile), but the elements inside the array "
      "remain mutable."),

    Q(F, "intermediate", J, "Strings are immutable in Java",
      """String word = "java";
word.toUpperCase();
System.out.println(word);""",
      "What does this print, why didn't word change to JAVA, and how do you fix it?",
      [("prints java (in lowercase)", ["java", "lowercase"], 2),
       ("Java Strings are immutable: toUpperCase() returns a new String and leaves word unchanged because the return value is ignored", ["immutab", "new string", "return value", "ignored"], 1.5),
       ("fix: assign word = word.toUpperCase()", ["word = word.touppercase()"], 1)],
      [("thinks it prints JAVA", ["prints java in uppercase", "prints JAVA"], "String methods never mutate the original String in place; they return a new String.")],
      "It prints java. Strings in Java are immutable: `word.toUpperCase()` creates and returns a new String "
      "\"JAVA\" without modifying `word`, and because the return value is not saved, it is discarded. Fix it by "
      "writing `word = word.toUpperCase();`."),

    Q(F, "intermediate", J, "Short-circuit guard against division by zero in Java",
      """int count = 0;
int total = 50;
if (count != 0 && total / count > 10) {
    System.out.println("high");
} else {
    System.out.println("safe");
}""",
      "What does this print, and why doesn't total / count throw ArithmeticException?",
      [("prints safe", ["safe", "prints safe"], 2),
       ("&& short-circuits: because count != 0 is false, Java never evaluates the right-hand side total / count > 10", ["short-circuit", "never evaluat", "not evaluated", "left side is false"], 1.5)],
      [],
      "It prints safe. Because `count` is 0, the left side `count != 0` evaluates to false, and Java's short-circuit "
      "`&&` operator skips evaluating `total / count > 10`, avoiding an `ArithmeticException: / by zero`."),

    Q(F, "intermediate", J, "Missing break in a Java switch statement",
      """int code = 1;
String out = "";
switch (code) {
    case 1:
        out += "A";
    case 2:
        out += "B";
        break;
    default:
        out += "C";
}
System.out.println(out);""",
      "What does this print, why, and how do you fix it if case 1 should only produce A?",
      [("prints AB", ["ab", "prints ab"], 2),
       ("case 1 has no break statement, so execution falls through into case 2 until it hits case 2's break", ["fall-through", "falls through", "fall through", "no break", "missing break"], 1.5)],
      [("thinks it prints A", ["only a"], "In a traditional switch statement, execution falls through to the next case unless stopped by break (or switch -> arrows).")],
      "It prints AB. Because `case 1:` has no `break;`, execution falls through directly into `case 2:`, appends "
      "\"B\", and then stops at `case 2`'s `break;`. Add `break;` at the end of `case 1` (or use `case 1 ->` switch "
      "rule syntax)."),

    # ── Advanced (8) ────────────────────────────────────────────────────────
    Q(F, "advanced", J, "try / catch / finally execution order",
      """static String run(int x) {
    try {
        int r = 10 / x;
        return "ok:" + r;
    } catch (ArithmeticException e) {
        return "err";
    } finally {
        System.out.print("done ");
    }
}
public static void main(String[] args) {
    System.out.println(run(0));
}""",
      "What is the exact output of main, and when does the finally block run relative to return \"err\"?",
      [("prints done err", ["done err"], 2),
       ("the finally block runs before the method actually returns to main, even when try or catch executes a return statement", ["finally", "before", "always runs", "even when"], 1.5)],
      [("thinks return \"err\" skips finally", ["skips finally", "only err"], "In Java, finally always executes before control leaves the try/catch via return or throw.")],
      "It prints done err. Dividing 10 by 0 throws `ArithmeticException`, entering `catch`, which prepares to return "
      "\"err\". Before `run(0)` actually returns that value to `main`, the `finally` block executes and prints "
      "`done `, followed by `println` printing `err`."),

    Q(F, "advanced", J, "Integer caching trap: == on Integer 100 vs 200",
      """Integer a = 100, b = 100;
Integer c = 200, d = 200;
System.out.println((a == b) + " " + (c == d));""",
      "What does this print, why do 100 and 200 behave differently with ==, and how should boxed Integers be compared?",
      [("prints true false", ["true false"], 2),
       ("Integer.valueOf caches boxed values from -128 to 127 so a and b share one object, while 200 is outside the cache and allocates two distinct Integer objects", ["cache", "-128", "127", "two objects", "reference"], 1.5),
       ("compare boxed Integers with .equals() (or unbox to primitive int)", ["equals", "intvalue", "primitive int"], 1)],
      [("thinks both are true", ["true true"], "Integer is a reference type; == compares object identity, which only matches inside the -128..127 cache.")],
      "It prints true false. Autoboxing calls `Integer.valueOf`, which caches instances for `-128` through `127`, so "
      "`a` and `b` point to the same cached `Integer(100)`. For `200`, two separate `Integer` objects are allocated "
      "and `c == d` compares their references (false). Always use `c.equals(d)` (or `int` primitives) to compare values."),

    Q(F, "advanced", J, "Autoboxing a null Integer throws NullPointerException",
      """Integer bonus = null;
int base = 50;
int total = base + bonus;
System.out.println(total);""",
      "What happens when int total = base + bonus runs, and why?",
      [("throws NullPointerException at runtime", ["nullpointerexception", "npe", "throws"], 2),
       ("to add int and Integer, Java auto-unboxes bonus by calling bonus.intValue(), which fails when bonus is null", ["unbox", "intvalue", "null"], 1.5)],
      [("thinks null is treated as 0 (prints 50)", ["prints 50", "treated as 0"], "Java does not convert a null wrapper to 0; unboxing null calls .intValue() and throws NullPointerException.")],
      "It throws a `NullPointerException` at runtime. To evaluate `base + bonus`, Java automatically unboxes the "
      "`Integer` wrapper by calling `bonus.intValue()`; because `bonus` is `null`, that call dereferences `null`."),

    Q(F, "advanced", J, "Aliasing an ArrayList vs copying it",
      """import java.util.*;

List<String> a = new ArrayList<>(List.of("x", "y"));
List<String> b = a;
List<String> c = new ArrayList<>(a);
b.add("z");
System.out.println(a.size() + " " + c.size());""",
      "What does this print, and why does a.size() change while c.size() does not?",
      [("prints 3 2", ["3 2", "3 and 2"], 2),
       ("b = a aliases the exact same ArrayList as a so b.add(\"z\") mutates a, whereas new ArrayList<>(a) constructs a separate list copy for c", ["alias", "same list", "separate", "copy", "new arraylist"], 1.5)],
      [],
      "It prints 3 2. `List<String> b = a` copies the reference, so `a` and `b` point to the same `ArrayList` and "
      "`b.add(\"z\")` adds a third item to it. `new ArrayList<>(a)` copies the elements into a brand-new list `c` "
      "before `" "z\"` is added, so `c.size()` stays 2."),

    Q(F, "advanced", J, "ArrayList<Integer>: remove(int) vs remove(Object)",
      """import java.util.*;

List<Integer> nums = new ArrayList<>(List.of(10, 20, 30));
nums.remove(1);
nums.remove(Integer.valueOf(10));
System.out.println(nums);""",
      "What does this print, and why did nums.remove(1) remove 20 instead of looking for the number 1?",
      [("prints [30]", ["[30]"], 2),
       ("remove(int index) is overloaded with remove(Object o): passing a primitive int 1 calls remove(int index) and removes index 1 (20), while Integer.valueOf(10) calls remove(Object) and removes the value 10", ["overload", "index 1", "remove(int", "remove(object", "valueof"], 1.5)],
      [],
      "It prints [30]. `List` has two overloaded methods: `remove(int index)` and `remove(Object o)`. Passing the "
      "primitive `int` literal `1` selects `remove(int index)` and removes element at index 1 (`20`). Passing "
      "`Integer.valueOf(10)` selects `remove(Object)` and removes the element equal to `10`, leaving `[30]`."),

    Q(F, "advanced", J, "Closing resources safely with try-with-resources",
      """BufferedReader br = new BufferedReader(new FileReader(path));
String line = br.readLine();
if (line == null) {
    throw new IllegalStateException("empty file");
}
br.close();""",
      "What resource bug happens when the file is empty, and how do you fix it with modern Java?",
      [("when IllegalStateException is thrown, br.close() is skipped and the file descriptor leaks", ["leak", "skipped", "never closed", "not closed", "before br.close"], 2),
       ("fix: wrap BufferedReader in try (BufferedReader br = ...) { ... } (try-with-resources) so Java closes it automatically even on exception", ["try-with-resources", "try (", "autocloseable", "automatically"], 1.5)],
      [],
      "When `line == null`, `IllegalStateException` is thrown before `br.close()` is reached, leaking the underlying "
      "file handle. Wrap the declaration in a `try (BufferedReader br = new BufferedReader(new FileReader(path)))` "
      "try-with-resources block so Java closes `br` automatically whether the block finishes normally or throws."),

    Q(F, "advanced", J, "Silent 32-bit int overflow in Java",
      """int max = Integer.MAX_VALUE;
int next = max + 1;
System.out.println(next < 0);""",
      "What does this print, why doesn't max + 1 throw an exception, and how can you prevent or detect it?",
      [("prints true (next wraps around to Integer.MIN_VALUE, -2147483648)", ["true", "min_value", "-2147483648", "wrap", "overflow"], 2),
       ("Java's + operator on 32-bit signed int wraps silently in two's complement; use long or Math.addExact(max, 1) to throw ArithmeticException on overflow", ["long", "addexact", "two's complement", "silent"], 1.5)],
      [("thinks Java throws ArithmeticException on max + 1", ["throws arithmeticexception"], "Standard + on int never throws in Java; it wraps around silently unless you call Math.addExact.")],
      "It prints true. Java's 32-bit signed `int` arithmetic overflows silently in two's complement, wrapping "
      "`Integer.MAX_VALUE + 1` around to `Integer.MIN_VALUE` (`-2147483648`), which is negative. Use `long` for "
      "wider range or `Math.addExact(max, 1)` to throw `ArithmeticException` on overflow."),

    Q(F, "advanced", J, "Removing from an ArrayList inside a for-each loop",
      """import java.util.*;

List<String> tags = new ArrayList<>(List.of("bug", "wip", "ok"));
for (String t : tags) {
    if (t.equals("wip")) {
        tags.remove(t);
    }
}""",
      "What happens when this loop runs, why, and what is the clean Java fix?",
      [("throws ConcurrentModificationException", ["concurrentmodificationexception", "throws"], 2),
       ("mutating the list directly via tags.remove(t) while its internal Iterator is iterating changes modCount and invalidates the iterator", ["iterator", "modcount", "while iterating"], 1.5),
       ("fix: use tags.removeIf(t -> t.equals(\"wip\")) or an explicit Iterator.remove()", ["removeif", "iterator.remove"], 1)],
      [],
      "It throws `ConcurrentModificationException`. The enhanced `for-each` loop uses an `Iterator` that checks "
      "the list's structural modification count on each step; calling `tags.remove(t)` directly on the list "
      "invalidates the iterator. Fix it with `tags.removeIf(t -> t.equals(\"wip\"));` (or `Iterator.remove()`)."),
]
