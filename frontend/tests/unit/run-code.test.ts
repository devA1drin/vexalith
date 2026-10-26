/**
 * Unit tests for how learner code is wrapped before it runs in the browser.
 * Run with `npm test` (compiles with tsc, then uses Node's built-in test runner).
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  cppProgram,
  cppSource,
  exampleCall,
  hasCppMain,
  javaCompileMessage,
  javaLayout,
  javaMain,
  javaProgram,
  phpProgram,
  phpSource,
  phpTidy,
} from "../../src/lib/harness";
import { splitPhpOutput } from "../../src/lib/runner-php";
import { OUTPUT_LIMIT, outputCollector } from "../../src/lib/runner";

const SIG = { params: ["int[]"], returns: "int" };

test("C++: finds a real main() and ignores one in a comment", () => {
  assert.equal(hasCppMain("int main() {\n  return 0;\n}"), true);
  assert.equal(hasCppMain("int main(int argc, char** argv) {}"), true);
  assert.equal(hasCppMain("// int main() is not needed\nint total(int x) { return x; }"), false);
});

test("C++: common headers come first and line numbers stay on the learner's code", () => {
  const src = cppSource("using namespace std;\nint main() { cout << 1; }");
  assert.match(src, /#include <iostream>/);
  assert.match(src, /#line 1 "main\.cpp"\nusing namespace std;/);
});

test("C++: a learner's main() is moved out of the way when the tests run", () => {
  const prog = cppProgram("int total(std::vector<int> v) { return 0; }\nint main() { return 0; }", "total", SIG, [{ args: [[1, 2]] }]);
  assert.match(prog, /#define main vx_learner_main\n#line 1 "main\.cpp"/);
  assert.match(prog, /#undef main/);
  const learner = prog.indexOf("int main() { return 0; }");
  assert.ok(learner > prog.indexOf("#define main") && learner < prog.indexOf("#undef main"), "the learner's main is renamed");
  assert.ok(prog.lastIndexOf("int main() {") > prog.indexOf("#undef main"), "the test runner's main comes after");
});

test("Java: a whole program in public class Main", () => {
  const code = "import java.util.*;\npublic class Main {\n  static int total(int[] a) { return 0; }\n  public static void main(String[] args) {}\n}";
  assert.deepEqual(javaLayout(code, "total"), { file: "Main.java", target: "Main", mainClass: "Main" });
});

test("Java: the starter layout, and comments or strings don't confuse it", () => {
  const code = '// class Fake { static void main(String[] a) {} }\nclass Solution {\n  static int total(int[] nums) {\n    String s = "static void main(";\n    return 0;\n  }\n}';
  assert.deepEqual(javaLayout(code, "total"), { file: "Solution.java", target: "Solution", mainClass: null });
  assert.equal(javaLayout("class Solution { }", "total").target, null);
});

test("Java: the test runner calls the class that holds the method", () => {
  const main = javaMain("total", SIG, [{ args: [[1, 2, 3]] }], 4000, "/files/out.txt", "Main", "Main.java");
  assert.match(main, /public class VxMain \{/);
  assert.match(main, /vxRun\(0, \(\) -> Main\.total\(new int\[\]\{1, 2, 3\}\)\);/);
});

test("Java: program mode runs main() with the typed input on System.in", () => {
  const prog = javaProgram("Main", 'Ada\n"21"\n', 10000, "/files/out.txt", "Main.java");
  assert.match(prog, /Main\.main\(new String\[0\]\);/);
  assert.ok(prog.includes(JSON.stringify('Ada\n"21"\n')), "stdin is embedded as an escaped string");
  assert.match(prog, /checkExit/);
});

test("Java: compile errors point at the learner's own file", () => {
  const msg = javaCompileMessage("/str/Main.java:3: error: incompatible types\n        int x = \"a\";\n1 error", "Main.java");
  assert.match(msg, /^Line 3: error: incompatible types/);
});

test("PHP: the input shim keeps line numbers and replaces readline()", () => {
  const code = "<?php\n$a = readline('Name? ');\n$b = $obj->readline();\necho $a;";
  const out = phpSource(code, "Ada\n");
  assert.equal(out.split("\n").length, code.split("\n").length);
  assert.match(out, /^<\?php if \(!defined\("STDIN"\)\)/);
  assert.match(out, /\$a = __vx_readline\('Name\? '\);/);
  assert.match(out, /\$obj->readline\(\);/);
  const noTag = phpSource("echo 'hi';");
  assert.match(noTag, /^<\?php .*echo 'hi';$/);
});

test("PHP: the test runner reports a missing function in plain words", () => {
  const prog = phpProgram("<?php\necho 'hi';", "total", SIG, [{ args: [[1]] }]);
  assert.match(prog, /function_exists\("total"\)/);
});

test("PHP: errors, warnings and printed output are told apart", () => {
  const raw = "start\n\nWarning: Undefined variable $nope in php-wasm run script on line 3\nmore\n\nFatal error: Uncaught Error: Call to undefined function f() in php-wasm run script:4\nStack trace:\n#0 {main}\n  thrown in php-wasm run script on line 4\n";
  const r = splitPhpOutput(raw);
  assert.equal(r.stdout.trim(), "start\nmore");
  assert.equal(r.stderr.trim(), "Warning: Undefined variable $nope (line 3)");
  assert.equal(r.fatal, "Error: Call to undefined function f() (line 4)");
  assert.equal(phpTidy("Parse error: syntax error in php-wasm run script on line 2"), "Parse error: syntax error (line 2)");
});

test("Hints: an example call in each language", () => {
  assert.equal(exampleCall("python", "total", [[1, 2, 3]]), "print(total([1, 2, 3]))");
  assert.equal(exampleCall("javascript", "total", [[1, 2, 3]]), "console.log(total([1, 2, 3]));");
  assert.equal(exampleCall("php", "total", [[1, 2, 3]]), 'echo json_encode(total([1, 2, 3])), "\\n";');
  assert.match(exampleCall("cpp", "total", [[1, 2, 3]], SIG), /cout << total\(\{1, 2, 3\}\) << endl;/);
  assert.match(exampleCall("java", "total", [[1, 2, 3]], SIG), /System\.out\.println\(Solution\.total\(new int\[\]\{1, 2, 3\}\)\);/);
  assert.equal(exampleCall("python", "ok", [true, null]), "print(ok(True, None))");
});

test("Output is capped per stream and marked as cut off", () => {
  const c = outputCollector();
  c.push("out", "x".repeat(OUTPUT_LIMIT - 1));
  c.push("out", "yy");
  c.push("err", "warn\n");
  assert.equal(c.value.stdout.length, OUTPUT_LIMIT);
  assert.equal(c.value.stderr, "warn\n");
  assert.equal(c.value.truncated, true);
});
