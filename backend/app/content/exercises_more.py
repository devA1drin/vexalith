"""C++, Java and PHP versions of the browser exercises.

They run in the learner's browser too: C++ is compiled by Clang compiled to
WebAssembly (YoWASP), Java by OpenJDK's javac on CheerpJ, PHP by php-wasm.
``signature`` tells the browser how to turn the JSON test inputs into
arguments for the typed languages: types are int, long, bool, str, int[], str[], map.
"""

from __future__ import annotations

# Shared test sets (same inputs/answers in every language).
T = {
    "sum": [([[1, 2, 3]], 6), ([[]], 0), ([[-5, 5, 10]], 10), ([[100]], 100), ([[0, 0, 0]], 0)],
    "reverse": [(["abc"], "cba"), (["racecar"], "racecar"), ([""], ""), (["Hi!"], "!iH")],
    "vowels": [(["hello"], 2), (["AEIOU"], 5), (["rhythm"], 0), ([""], 0), (["Programming is fun"], 5)],
    "fizzbuzz": [([5], ["1", "2", "Fizz", "4", "Buzz"]), ([1], ["1"]),
                 ([15], ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]), ([0], [])],
    "largest": [([[3, 9, 2]], 9), ([[-4, -2, -7]], -2), ([[5]], 5), ([[1, 1, 1]], 1)],
    "palindrome": [(["racecar"], True), (["hello"], False), (["Never odd or even"], True), ([""], True), (["ab"], False)],
    "words": [(["the cat the hat"], {"the": 2, "cat": 1, "hat": 1}), (["Go go GO"], {"go": 3}), (["one"], {"one": 1})],
    "unique": [([[1, 2, 1, 3, 2]], [1, 2, 3]), ([[]], []), ([[7, 7, 7]], [7]), ([[5, 4, 5, 4, 3]], [5, 4, 3])],
    "two_sum": [([[2, 7, 11, 15], 9], [0, 1]), ([[3, 2, 4], 6], [1, 2]), ([[1, 5, 5], 10], [1, 2]), ([[0, -3, 8, 3], 0], [1, 3])],
    "fib": [([0], 0), ([1], 1), ([10], 55), ([30], 832040), ([50], 12586269025)],
    "search": [([[1, 3, 5, 7, 9], 7], 3), ([[1, 3, 5], 4], -1), ([[], 1], -1), ([[2], 2], 0), ([list(range(0, 1000, 2)), 998], 499)],
}

# concept -> (difficulty, title, topic, test set, params, returns)
CONCEPTS = {
    "sum-list": ("beginner", "Add up a list", "Loops", "sum", ["int[]"], "int"),
    "reverse-string": ("beginner", "Reverse a word", "Strings", "reverse", ["str"], "str"),
    "count-vowels": ("beginner", "Count the vowels", "Strings", "vowels", ["str"], "int"),
    "fizzbuzz": ("beginner", "FizzBuzz list", "Loops & conditions", "fizzbuzz", ["int"], "str[]"),
    "largest": ("beginner", "Find the largest number", "Loops", "largest", ["int[]"], "int"),
    "palindrome": ("intermediate", "Is it a palindrome?", "Strings", "palindrome", ["str"], "bool"),
    "word-count": ("intermediate", "Count words", "Dictionaries & maps", "words", ["str"], "map"),
    "unique": ("intermediate", "Remove duplicates, keep order", "Lists & sets", "unique", ["int[]"], "int[]"),
    "two-sum": ("intermediate", "Two numbers that add up", "Hash maps", "two_sum", ["int[]", "int"], "int[]"),
    "fibonacci": ("intermediate", "Fibonacci number", "Loops & math", "fib", ["int"], "long"),
    "binary-search": ("advanced", "Binary search", "Searching", "search", ["int[]", "int"], "int"),
}

# language -> concept -> (function, description, starter, solution)
CPP = {
    "sum-list": ("total", "Write `int total(vector<int> nums)` that returns the sum of all numbers. An empty vector adds up to 0. Use a loop.",
        "#include <vector>\nusing namespace std;\n\nint total(vector<int> nums) {\n    int result = 0;\n    // add each number to result\n    return result;\n}\n",
        "#include <vector>\nusing namespace std;\n\nint total(vector<int> nums) {\n    int result = 0;\n    for (int n : nums) result += n;\n    return result;\n}\n"),
    "reverse-string": ("reverse_text", "Write `string reverse_text(string text)` that returns the text backwards, so \"abc\" becomes \"cba\".",
        "#include <string>\nusing namespace std;\n\nstring reverse_text(string text) {\n    return text;\n}\n",
        "#include <string>\nusing namespace std;\n\nstring reverse_text(string text) {\n    return string(text.rbegin(), text.rend());\n}\n"),
    "count-vowels": ("count_vowels", "Write `int count_vowels(string text)` that returns how many vowels (a, e, i, o, u) are in the text. Upper-case vowels count too.",
        "#include <string>\nusing namespace std;\n\nint count_vowels(string text) {\n    int count = 0;\n    return count;\n}\n",
        "#include <string>\n#include <cctype>\nusing namespace std;\n\nint count_vowels(string text) {\n    int count = 0;\n    for (char c : text) {\n        char l = tolower(c);\n        if (l == 'a' || l == 'e' || l == 'i' || l == 'o' || l == 'u') count++;\n    }\n    return count;\n}\n"),
    "fizzbuzz": ("fizzbuzz", "Write `vector<string> fizzbuzz(int n)` that returns the strings for 1..n: \"Fizz\" for multiples of 3, \"Buzz\" for multiples of 5, \"FizzBuzz\" for both, otherwise the number as text (to_string helps).",
        "#include <string>\n#include <vector>\nusing namespace std;\n\nvector<string> fizzbuzz(int n) {\n    vector<string> out;\n    for (int i = 1; i <= n; i++) {\n        // your code here\n    }\n    return out;\n}\n",
        "#include <string>\n#include <vector>\nusing namespace std;\n\nvector<string> fizzbuzz(int n) {\n    vector<string> out;\n    for (int i = 1; i <= n; i++) {\n        if (i % 15 == 0) out.push_back(\"FizzBuzz\");\n        else if (i % 3 == 0) out.push_back(\"Fizz\");\n        else if (i % 5 == 0) out.push_back(\"Buzz\");\n        else out.push_back(to_string(i));\n    }\n    return out;\n}\n"),
    "largest": ("largest", "Write `int largest(vector<int> nums)` that returns the biggest number in a non-empty vector, without max_element.",
        "#include <vector>\nusing namespace std;\n\nint largest(vector<int> nums) {\n    int best = nums[0];\n    return best;\n}\n",
        "#include <vector>\nusing namespace std;\n\nint largest(vector<int> nums) {\n    int best = nums[0];\n    for (int n : nums) if (n > best) best = n;\n    return best;\n}\n"),
    "palindrome": ("is_palindrome", "Write `bool is_palindrome(string text)` that returns true when the text reads the same forwards and backwards, ignoring spaces and upper/lower case.",
        "#include <string>\nusing namespace std;\n\nbool is_palindrome(string text) {\n    return false;\n}\n",
        "#include <string>\n#include <cctype>\nusing namespace std;\n\nbool is_palindrome(string text) {\n    string c;\n    for (char ch : text) if (ch != ' ') c += tolower(ch);\n    return c == string(c.rbegin(), c.rend());\n}\n"),
    "word-count": ("word_count", "Write `map<string, int> word_count(string text)` that maps each lower-case word to how many times it appears. Words are separated by spaces.",
        "#include <map>\n#include <string>\nusing namespace std;\n\nmap<string, int> word_count(string text) {\n    map<string, int> counts;\n    return counts;\n}\n",
        "#include <map>\n#include <sstream>\n#include <string>\n#include <cctype>\nusing namespace std;\n\nmap<string, int> word_count(string text) {\n    map<string, int> counts;\n    for (char &c : text) c = tolower(c);\n    istringstream in(text);\n    string w;\n    while (in >> w) counts[w]++;\n    return counts;\n}\n"),
    "unique": ("unique_items", "Write `vector<int> unique_items(vector<int> items)` that returns the items without duplicates, keeping the first time each one appears.",
        "#include <vector>\nusing namespace std;\n\nvector<int> unique_items(vector<int> items) {\n    return items;\n}\n",
        "#include <set>\n#include <vector>\nusing namespace std;\n\nvector<int> unique_items(vector<int> items) {\n    set<int> seen;\n    vector<int> out;\n    for (int x : items) if (seen.insert(x).second) out.push_back(x);\n    return out;\n}\n"),
    "two-sum": ("two_sum", "Write `vector<int> two_sum(vector<int> nums, int target)` that returns the indexes {i, j} (i < j) of the two numbers that add up to target. There is always exactly one answer.",
        "#include <vector>\nusing namespace std;\n\nvector<int> two_sum(vector<int> nums, int target) {\n    return {0, 0};\n}\n",
        "#include <unordered_map>\n#include <vector>\nusing namespace std;\n\nvector<int> two_sum(vector<int> nums, int target) {\n    unordered_map<int, int> seen;\n    for (int j = 0; j < (int)nums.size(); j++) {\n        if (seen.count(target - nums[j])) return {seen[target - nums[j]], j};\n        seen[nums[j]] = j;\n    }\n    return {};\n}\n"),
    "fibonacci": ("fib", "Write `long long fib(int n)` that returns the n-th Fibonacci number, where fib(0) = 0 and fib(1) = 1. Use a loop so n = 50 is instant (an int is too small, so use long long).",
        "long long fib(int n) {\n    return n;\n}\n",
        "long long fib(int n) {\n    long long a = 0, b = 1;\n    for (int i = 0; i < n; i++) {\n        long long t = a + b;\n        a = b;\n        b = t;\n    }\n    return a;\n}\n"),
    "binary-search": ("search", "Write `int search(vector<int> nums, int target)` for a sorted vector that returns the index of target, or -1 if it isn't there. Cut the range in half each step.",
        "#include <vector>\nusing namespace std;\n\nint search(vector<int> nums, int target) {\n    int lo = 0, hi = (int)nums.size() - 1;\n    return -1;\n}\n",
        "#include <vector>\nusing namespace std;\n\nint search(vector<int> nums, int target) {\n    int lo = 0, hi = (int)nums.size() - 1;\n    while (lo <= hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n    }\n    return -1;\n}\n"),
}

_J = "import java.util.*;\n\nclass Solution {\n"
JAVA = {
    "sum-list": ("total", "Write `static int total(int[] nums)` in class Solution that returns the sum of all numbers. An empty array adds up to 0. Use a loop.",
        _J + "    static int total(int[] nums) {\n        int result = 0;\n        // add each number to result\n        return result;\n    }\n}\n",
        _J + "    static int total(int[] nums) {\n        int result = 0;\n        for (int n : nums) result += n;\n        return result;\n    }\n}\n"),
    "reverse-string": ("reverse", "Write `static String reverse(String text)` that returns the text backwards, so \"abc\" becomes \"cba\".",
        _J + "    static String reverse(String text) {\n        return text;\n    }\n}\n",
        _J + "    static String reverse(String text) {\n        return new StringBuilder(text).reverse().toString();\n    }\n}\n"),
    "count-vowels": ("countVowels", "Write `static int countVowels(String text)` that returns how many vowels (a, e, i, o, u) are in the text. Upper-case vowels count too.",
        _J + "    static int countVowels(String text) {\n        int count = 0;\n        return count;\n    }\n}\n",
        _J + "    static int countVowels(String text) {\n        int count = 0;\n        for (char c : text.toLowerCase().toCharArray()) if (\"aeiou\".indexOf(c) >= 0) count++;\n        return count;\n    }\n}\n"),
    "fizzbuzz": ("fizzbuzz", "Write `static List<String> fizzbuzz(int n)` that returns the strings for 1..n: \"Fizz\" for multiples of 3, \"Buzz\" for multiples of 5, \"FizzBuzz\" for both, otherwise the number as text.",
        _J + "    static List<String> fizzbuzz(int n) {\n        List<String> out = new ArrayList<>();\n        for (int i = 1; i <= n; i++) {\n            // your code here\n        }\n        return out;\n    }\n}\n",
        _J + "    static List<String> fizzbuzz(int n) {\n        List<String> out = new ArrayList<>();\n        for (int i = 1; i <= n; i++) {\n            if (i % 15 == 0) out.add(\"FizzBuzz\");\n            else if (i % 3 == 0) out.add(\"Fizz\");\n            else if (i % 5 == 0) out.add(\"Buzz\");\n            else out.add(String.valueOf(i));\n        }\n        return out;\n    }\n}\n"),
    "largest": ("largest", "Write `static int largest(int[] nums)` that returns the biggest number in a non-empty array, without Math.max.",
        _J + "    static int largest(int[] nums) {\n        int best = nums[0];\n        return best;\n    }\n}\n",
        _J + "    static int largest(int[] nums) {\n        int best = nums[0];\n        for (int n : nums) if (n > best) best = n;\n        return best;\n    }\n}\n"),
    "palindrome": ("isPalindrome", "Write `static boolean isPalindrome(String text)` that returns true when the text reads the same forwards and backwards, ignoring spaces and upper/lower case.",
        _J + "    static boolean isPalindrome(String text) {\n        return false;\n    }\n}\n",
        _J + "    static boolean isPalindrome(String text) {\n        String c = text.replace(\" \", \"\").toLowerCase();\n        return c.equals(new StringBuilder(c).reverse().toString());\n    }\n}\n"),
    "word-count": ("wordCount", "Write `static Map<String, Integer> wordCount(String text)` that maps each lower-case word to how many times it appears. Words are separated by spaces.",
        _J + "    static Map<String, Integer> wordCount(String text) {\n        Map<String, Integer> counts = new HashMap<>();\n        return counts;\n    }\n}\n",
        _J + "    static Map<String, Integer> wordCount(String text) {\n        Map<String, Integer> counts = new HashMap<>();\n        for (String w : text.toLowerCase().split(\" \")) {\n            if (!w.isEmpty()) counts.put(w, counts.getOrDefault(w, 0) + 1);\n        }\n        return counts;\n    }\n}\n"),
    "unique": ("unique", "Write `static List<Integer> unique(int[] items)` that returns the items without duplicates, keeping the first time each one appears.",
        _J + "    static List<Integer> unique(int[] items) {\n        List<Integer> out = new ArrayList<>();\n        return out;\n    }\n}\n",
        _J + "    static List<Integer> unique(int[] items) {\n        Set<Integer> seen = new LinkedHashSet<>();\n        for (int x : items) seen.add(x);\n        return new ArrayList<>(seen);\n    }\n}\n"),
    "two-sum": ("twoSum", "Write `static int[] twoSum(int[] nums, int target)` that returns the indexes {i, j} (i < j) of the two numbers that add up to target. There is always exactly one answer. A HashMap makes it one pass.",
        _J + "    static int[] twoSum(int[] nums, int target) {\n        return new int[]{0, 0};\n    }\n}\n",
        _J + "    static int[] twoSum(int[] nums, int target) {\n        Map<Integer, Integer> seen = new HashMap<>();\n        for (int j = 0; j < nums.length; j++) {\n            Integer i = seen.get(target - nums[j]);\n            if (i != null) return new int[]{i, j};\n            seen.put(nums[j], j);\n        }\n        return new int[0];\n    }\n}\n"),
    "fibonacci": ("fib", "Write `static long fib(int n)` that returns the n-th Fibonacci number, where fib(0) = 0 and fib(1) = 1. Use a loop so n = 50 is instant (an int is too small, so use long).",
        _J + "    static long fib(int n) {\n        return n;\n    }\n}\n",
        _J + "    static long fib(int n) {\n        long a = 0, b = 1;\n        for (int i = 0; i < n; i++) {\n            long t = a + b;\n            a = b;\n            b = t;\n        }\n        return a;\n    }\n}\n"),
    "binary-search": ("search", "Write `static int search(int[] nums, int target)` for a sorted array that returns the index of target, or -1 if it isn't there. Cut the range in half each step.",
        _J + "    static int search(int[] nums, int target) {\n        int lo = 0, hi = nums.length - 1;\n        return -1;\n    }\n}\n",
        _J + "    static int search(int[] nums, int target) {\n        int lo = 0, hi = nums.length - 1;\n        while (lo <= hi) {\n            int mid = (lo + hi) / 2;\n            if (nums[mid] == target) return mid;\n            if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n        }\n        return -1;\n    }\n}\n"),
}

PHP = {
    "sum-list": ("total", "Write `total($nums)` that returns the sum of all numbers in the array. An empty array adds up to 0. Use a loop instead of array_sum().",
        "<?php\nfunction total($nums) {\n    $result = 0;\n    // add each number to $result\n    return $result;\n}\n",
        "<?php\nfunction total($nums) {\n    $result = 0;\n    foreach ($nums as $n) {\n        $result += $n;\n    }\n    return $result;\n}\n"),
    "reverse-string": ("reverse_text", "Write `reverse_text($text)` that returns the text backwards, so 'abc' becomes 'cba'.",
        "<?php\nfunction reverse_text($text) {\n    return $text;\n}\n",
        "<?php\nfunction reverse_text($text) {\n    return strrev($text);\n}\n"),
    "count-vowels": ("count_vowels", "Write `count_vowels($text)` that returns how many vowels (a, e, i, o, u) are in the text. Upper-case vowels count too.",
        "<?php\nfunction count_vowels($text) {\n    $count = 0;\n    return $count;\n}\n",
        "<?php\nfunction count_vowels($text) {\n    return preg_match_all('/[aeiou]/i', $text);\n}\n"),
    "fizzbuzz": ("fizzbuzz", "Write `fizzbuzz($n)` that returns an array of strings for 1..n: 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for both, otherwise the number as text.",
        "<?php\nfunction fizzbuzz($n) {\n    $out = [];\n    for ($i = 1; $i <= $n; $i++) {\n        // your code here\n    }\n    return $out;\n}\n",
        "<?php\nfunction fizzbuzz($n) {\n    $out = [];\n    for ($i = 1; $i <= $n; $i++) {\n        if ($i % 15 == 0) $out[] = 'FizzBuzz';\n        elseif ($i % 3 == 0) $out[] = 'Fizz';\n        elseif ($i % 5 == 0) $out[] = 'Buzz';\n        else $out[] = (string)$i;\n    }\n    return $out;\n}\n"),
    "largest": ("largest", "Write `largest($nums)` that returns the biggest number in a non-empty array, without max().",
        "<?php\nfunction largest($nums) {\n    $best = $nums[0];\n    return $best;\n}\n",
        "<?php\nfunction largest($nums) {\n    $best = $nums[0];\n    foreach ($nums as $n) {\n        if ($n > $best) $best = $n;\n    }\n    return $best;\n}\n"),
    "palindrome": ("is_palindrome", "Write `is_palindrome($text)` that returns true when the text reads the same forwards and backwards, ignoring spaces and upper/lower case.",
        "<?php\nfunction is_palindrome($text) {\n    return false;\n}\n",
        "<?php\nfunction is_palindrome($text) {\n    $c = strtolower(str_replace(' ', '', $text));\n    return $c === strrev($c);\n}\n"),
    "word-count": ("word_count", "Write `word_count($text)` that returns an array mapping each lower-case word to how many times it appears. Words are separated by spaces.",
        "<?php\nfunction word_count($text) {\n    $counts = [];\n    return $counts;\n}\n",
        "<?php\nfunction word_count($text) {\n    $counts = [];\n    foreach (explode(' ', strtolower($text)) as $w) {\n        if ($w === '') continue;\n        $counts[$w] = ($counts[$w] ?? 0) + 1;\n    }\n    return $counts;\n}\n"),
    "unique": ("unique_items", "Write `unique_items($items)` that returns the items without duplicates, keeping the first time each one appears (as a normal list, re-numbered from 0).",
        "<?php\nfunction unique_items($items) {\n    return $items;\n}\n",
        "<?php\nfunction unique_items($items) {\n    $out = [];\n    foreach ($items as $x) {\n        if (!in_array($x, $out, true)) $out[] = $x;\n    }\n    return $out;\n}\n"),
    "two-sum": ("two_sum", "Write `two_sum($nums, $target)` that returns the indexes [i, j] (i < j) of the two numbers that add up to target. There is always exactly one answer.",
        "<?php\nfunction two_sum($nums, $target) {\n    return [0, 0];\n}\n",
        "<?php\nfunction two_sum($nums, $target) {\n    $seen = [];\n    foreach ($nums as $j => $n) {\n        if (isset($seen[$target - $n])) return [$seen[$target - $n], $j];\n        $seen[$n] = $j;\n    }\n    return [];\n}\n"),
    "fibonacci": ("fib", "Write `fib($n)` that returns the n-th Fibonacci number, where fib(0) = 0 and fib(1) = 1. Use a loop so n = 50 is instant.",
        "<?php\nfunction fib($n) {\n    return $n;\n}\n",
        "<?php\nfunction fib($n) {\n    $a = 0;\n    $b = 1;\n    for ($i = 0; $i < $n; $i++) {\n        [$a, $b] = [$b, $a + $b];\n    }\n    return $a;\n}\n"),
    "binary-search": ("search", "Write `search($nums, $target)` for a sorted array that returns the index of target, or -1 if it isn't there. Cut the range in half each step (intdiv helps).",
        "<?php\nfunction search($nums, $target) {\n    $lo = 0;\n    $hi = count($nums) - 1;\n    return -1;\n}\n",
        "<?php\nfunction search($nums, $target) {\n    $lo = 0;\n    $hi = count($nums) - 1;\n    while ($lo <= $hi) {\n        $mid = intdiv($lo + $hi, 2);\n        if ($nums[$mid] == $target) return $mid;\n        if ($nums[$mid] < $target) $lo = $mid + 1; else $hi = $mid - 1;\n    }\n    return -1;\n}\n"),
}

PREFIX = {"cpp": "cpp", "java": "java", "php": "php"}
TIMEOUTS = {"cpp": 4000, "java": 6000, "php": 4000}


def build(make) -> list[dict]:
    out = []
    for language, table in (("cpp", CPP), ("java", JAVA), ("php", PHP)):
        for concept, (fn, desc, starter, solution) in table.items():
            difficulty, title, topic, tests, params, returns = CONCEPTS[concept]
            e = make(f"{PREFIX[language]}-{concept}", language, difficulty, title, desc, fn, starter, solution,
                     T[tests], timeout_ms=TIMEOUTS[language])
            e["topic"] = topic
            e["signature"] = {"params": params, "returns": returns}
            out.append(e)
    return out
