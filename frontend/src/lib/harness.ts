/**
 * Turns a learner's C++, Java or PHP code plus the test inputs into one program
 * that calls their function once per test and prints marked results, and reads
 * those results back. The test inputs are JSON; `signature` says which types
 * the typed languages need (int, long, bool, str, int[], str[], map).
 */
import type { RunResult, Signature, TestInput } from "./runner";



const M = "\u0001VX|"; // marker that learner output will not contain by accident

/** Read `\u0001VX|B|i`, `|R|i|json`, `|E|i|json-string`, `|O|i|json-string` lines. */
export function parseMarked(text: string, n: number): { results: RunResult[]; started: number; extra: string } {
  const results: RunResult[] = Array.from({ length: n }, () => ({ output: null, error: "Didn't run", stdout: "", ms: 0 }));
  let current = -1;
  let started = -1;
  let extra = "";
  for (const line of text.split("\n")) {
    const at = line.indexOf(M);
    if (at < 0) {
      if (current >= 0 && current < n) results[current].stdout += line + "\n";
      else if (line.trim()) extra += line + "\n";
      continue;
    }
    if (at > 0 && current >= 0 && current < n) results[current].stdout += line.slice(0, at); // print without newline
    const [kind, idx, ...rest] = line.slice(at + M.length).split("|");
    const i = Number(idx);
    const payload = rest.join("|");
    if (!(i >= 0 && i < n)) continue;
    if (kind === "B") {
      current = i;
      started = i;
      results[i] = { output: null, error: null, stdout: "", ms: 0 };
    } else if (kind === "R") {
      results[i].output = payload;
    } else if (kind === "E") {
      results[i].error = safeString(payload);
    } else if (kind === "O") {
      results[i].stdout = safeString(payload);
    }
  }
  for (const r of results) {
    r.stdout = r.stdout.slice(0, 4000);
    if (r.error === null && r.output === null) r.error = "Your code stopped before it returned an answer.";
  }
  return { results, started, extra };
}

function safeString(s: string): string {
  try {
    const v = JSON.parse(s);
    return typeof v === "string" ? v : s;
  } catch {
    return s;
  }
}

// ---------- C++ ----------

const CPP_TYPES: Record<string, (v: unknown) => string> = {
  int: (v) => String(v),
  long: (v) => `${v}LL`,
  bool: (v) => (v ? "true" : "false"),
  str: (v) => `std::string(${JSON.stringify(v)})`,
  "int[]": (v) => `std::vector<int>{${(v as number[]).join(", ")}}`,
  "str[]": (v) => `std::vector<std::string>{${(v as string[]).map((s) => JSON.stringify(s)).join(", ")}}`,
};

/**
 * Common headers go in front of the learner's code (so `cout` works even without
 * `#include <iostream>`), then `#line 1` keeps compiler line numbers on their code.
 */
const CPP_PRELUDE = `#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <string>
#include <vector>
`;

/** True when the code has its own entry point: `int main(` (comments ignored). */
export function hasCppMain(code: string): boolean {
  return /\bint\s+main\s*\(/.test(stripComments(code));
}

/** The learner's whole program, compiled as it is (for "Run my code"). */
export function cppSource(code: string): string {
  return `${CPP_PRELUDE}#line 1 "main.cpp"\n${code}\n`;
}

export function cppProgram(code: string, fn: string, sig: Signature, tests: TestInput[]): string {
  const calls = tests
    .map((t, i) => {
      const args = t.args.map((a, k) => CPP_TYPES[sig.params[k]](a)).join(", ");
      return `  std::cout << "\\001VX|B|${i}" << std::endl;\n  { auto vx_r = ${fn}(${args}); std::cout << "\\n\\001VX|R|${i}|" << vx_::j(vx_r) << std::endl; }`;
    })
    .join("\n");
  // A learner's own main() is renamed out of the way so the tests can still call their function.
  return `${CPP_PRELUDE}#define main vx_learner_main
#line 1 "main.cpp"
${code}
#undef main
namespace vx_ {
inline std::string j(const std::string& s) {
  std::string o = "\\"";
  for (unsigned char c : s) {
    if (c == '"' || c == '\\\\') { o += '\\\\'; o += (char)c; }
    else if (c == '\\n') o += "\\\\n";
    else if (c < 0x20) { char b[8]; snprintf(b, sizeof b, "\\\\u%04x", c); o += b; }
    else o += (char)c;
  }
  return o + "\\"";
}
inline std::string j(const char* s) { return j(std::string(s)); }
inline std::string j(char c) { return j(std::string(1, c)); }
inline std::string j(bool v) { return v ? "true" : "false"; }
inline std::string j(int v) { return std::to_string(v); }
inline std::string j(long v) { return std::to_string(v); }
inline std::string j(long long v) { return std::to_string(v); }
inline std::string j(unsigned v) { return std::to_string(v); }
inline std::string j(unsigned long v) { return std::to_string(v); }
inline std::string j(unsigned long long v) { return std::to_string(v); }
inline std::string j(double v) { char b[64]; snprintf(b, sizeof b, "%.15g", v); return b; }
template <class T> std::string j(const std::vector<T>& v) {
  std::string o = "[";
  for (size_t i = 0; i < v.size(); i++) { if (i) o += ","; o += j((T)v[i]); }
  return o + "]";
}
template <class V> std::string j(const std::map<std::string, V>& m) {
  std::string o = "{";
  bool first = true;
  for (const auto& kv : m) { if (!first) o += ","; first = false; o += j(kv.first) + ":" + j(kv.second); }
  return o + "}";
}
}  // namespace vx_
int main() {
${calls}
  return 0;
}
`;
}

/** Make clang's messages beginner-friendly and point at the learner's own lines. */
export function cppCompileMessage(stderr: string): string {
  if (/redefinition of 'main'/.test(stderr)) {
    return "Please remove your main() function. The tests call your function for you.";
  }
  const lines = stderr
    .split("\n")
    .filter((l) => l.trim() && !l.includes("vx_") && !/^\d+ errors? generated/.test(l))
    .map((l) => l.replace(/^main\.cpp:(\d+):(\d+):/, "Line $1:"));
  return lines.slice(0, 12).join("\n") || "Your code didn't compile.";
}

// ---------- Java ----------

const JAVA_TYPES: Record<string, (v: unknown) => string> = {
  int: (v) => String(v),
  long: (v) => `${v}L`,
  bool: (v) => (v ? "true" : "false"),
  str: (v) => JSON.stringify(v),
  "int[]": (v) => `new int[]{${(v as number[]).join(", ")}}`,
  "str[]": (v) => `new String[]{${(v as string[]).map((s) => JSON.stringify(s)).join(", ")}}`,
};

/**
 * Java code can't be stopped from outside without freezing the page, so every
 * loop (while, for, do) gets a cheap time check:
 * a `VxGuard.tick()` call (at the top of a braced body, otherwise in the
 * condition). Strings, chars and comments are skipped.
 * Line numbers don't change.
 */
export function guardJavaLoops(src: string): string {
  let out = "";
  let i = 0;
  const n = src.length;
  const isWord = (c: string) => /[A-Za-z0-9_$]/.test(c);
  while (i < n) {
    const c = src[i];
    if (c === "/" && src[i + 1] === "/") {
      const e = src.indexOf("\n", i);
      const end = e < 0 ? n : e;
      out += src.slice(i, end);
      i = end;
      continue;
    }
    if (c === "/" && src[i + 1] === "*") {
      const e = src.indexOf("*/", i + 2);
      const end = e < 0 ? n : e + 2;
      out += src.slice(i, end);
      i = end;
      continue;
    }
    if (c === '"' || c === "'") {
      let k = i + 1;
      while (k < n && src[k] !== c) k += src[k] === "\\" ? 2 : 1;
      out += src.slice(i, k + 1);
      i = k + 1;
      continue;
    }
    if (src.startsWith("do", i) && (i === 0 || !isWord(src[i - 1])) && !isWord(src[i + 2] ?? "")) {
      let k = i + 2;
      while (k < n && /\s/.test(src[k])) k++;
      if (src[k] === "{") {
        out += src.slice(i, k + 1) + "VxGuard.tick();";
        i = k + 1;
        continue;
      }
    }
    const kw = src.startsWith("while", i) ? "while" : src.startsWith("for", i) ? "for" : null;
    if (kw && (i === 0 || !isWord(src[i - 1])) && !isWord(src[i + kw.length] ?? "")) {
      let k = i + kw.length;
      while (k < n && /\s/.test(src[k])) k++;
      if (src[k] === "(") {
        const close = matchParen(src, k);
        if (close > 0) {
          const inner = src.slice(k + 1, close);
          let b = close + 1;
          while (b < n && /\s/.test(src[b])) b++;
          if (src[b] === "{") {
            // Tick at the top of the body and leave the condition untouched, so
            // javac still treats `while (true)` as an endless loop (no "missing return").
            out += src.slice(i, b + 1) + "VxGuard.tick();";
            i = b + 1;
            continue;
          }
          out += src.slice(i, k + 1);
          if (kw === "while") {
            // A do-while tail with `true` is already guarded inside its body.
            out += inner.trim() === "true" && src[b] === ";" ? inner : `VxGuard.tick() && (${inner})`;
          } else {
            const parts = splitTopLevel(inner, ";");
            if (parts.length === 3) {
              const cond = parts[1].trim();
              out += `${parts[0]};VxGuard.tick() && (${cond || "true"});${parts[2]}`;
            } else {
              out += inner; // for-each loops over a finite collection
            }
          }
          out += ")";
          i = close + 1;
          continue;
        }
      }
    }
    out += c;
    i++;
  }
  return out;
}

function matchParen(s: string, open: number): number {
  let depth = 0;
  for (let k = open; k < s.length; k++) {
    const c = s[k];
    if (c === '"' || c === "'") {
      k++;
      while (k < s.length && s[k] !== c) k += s[k] === "\\" ? 2 : 1;
      continue;
    }
    if (c === "(") depth++;
    else if (c === ")" && --depth === 0) return k;
  }
  return -1;
}

function splitTopLevel(s: string, sep: string): string[] {
  const parts: string[] = [];
  let depth = 0;
  let last = 0;
  for (let k = 0; k < s.length; k++) {
    const c = s[k];
    if (c === '"' || c === "'") {
      k++;
      while (k < s.length && s[k] !== c) k += s[k] === "\\" ? 2 : 1;
      continue;
    }
    if ("([{".includes(c)) depth++;
    else if (")]}".includes(c)) depth--;
    else if (c === sep && depth === 0) {
      parts.push(s.slice(last, k));
      last = k + 1;
    }
  }
  parts.push(s.slice(last));
  return parts;
}

/** Blank out comments and string/char literals (same length), so regexes only see code. */
function stripComments(src: string): string {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " "))
    .replace(/\/\/[^\n]*/g, (m) => " ".repeat(m.length))
    .replace(/"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'/g, (m) => " ".repeat(m.length));
}

export type JavaLayout = {
  /** File the learner's code is saved as: javac needs `public class X` to live in X.java. */
  file: string;
  /** Class that declares the exercise method, if any. */
  target: string | null;
  /** Class with `static void main(String…)`, if any. */
  mainClass: string | null;
};

/** Work out the file name, the class holding the method, and the class with main(). */
export function javaLayout(code: string, fn?: string): JavaLayout {
  const src = stripComments(code);
  const classes = [...src.matchAll(/\b(?:class|interface|enum|record)\s+([A-Za-z_$][\w$]*)/g)].map((m) => ({ name: m[1], at: m.index ?? 0 }));
  const owner = (at: number) => classes.filter((c) => c.at < at).pop()?.name ?? null;
  const pub = /\bpublic\s+(?:(?:final|abstract|static)\s+)*(?:class|interface|enum|record)\s+([A-Za-z_$][\w$]*)/.exec(src);
  let target: string | null = null;
  if (fn) {
    const decl = new RegExp(`[\\w$>\\]]\\s+${fn}\\s*\\([^)]*\\)\\s*(?:throws[^{;]*)?\\{`).exec(src);
    if (decl) target = owner(decl.index);
  }
  const main = /\bstatic\s+(?:final\s+)?void\s+main\s*\(/.exec(src) ?? /\bvoid\s+static\s+main\s*\(/.exec(src);
  return { file: `${pub ? pub[1] : "Solution"}.java`, target, mainClass: main ? owner(main.index) : null };
}

const JAVA_GUARD = `class VxTimeout extends RuntimeException {}

class VxGuard {
  static long deadline = Long.MAX_VALUE;
  static boolean tick() {
    if (System.currentTimeMillis() > deadline) throw new VxTimeout();
    return true;
  }
}`;

/**
 * Where an exception happened in the learner's code: "(line N)" when the JVM knows
 * it, otherwise "(in Class.method)" (CheerpJ doesn't keep line numbers).
 */
const javaWhere = (file: string) => `  static String vxWhere(Throwable e) {
    for (StackTraceElement f : e.getStackTrace()) {
      if (${JSON.stringify(file)}.equals(f.getFileName()) && f.getLineNumber() > 0) return " (line " + f.getLineNumber() + ")";
      String c = f.getClassName();
      if (!c.startsWith("Vx") && !c.startsWith("java.") && !c.startsWith("javax.") && !c.startsWith("sun.") && !c.startsWith("jdk.")) {
        return " (in " + c + "." + f.getMethodName() + ")";
      }
    }
    return "";
  }`;

const JAVA_QUOTE = `  static String q(String s) {
    StringBuilder b = new StringBuilder("\\"");
    for (char c : s.toCharArray()) {
      if (c == '"' || c == '\\\\') b.append('\\\\').append(c);
      else if (c == '\\n') b.append("\\\\n");
      else if (c < 0x20) b.append(String.format("\\\\u%04x", (int) c));
      else b.append(c);
    }
    return b.append('"').toString();
  }`;

export function javaMain(
  fn: string,
  sig: Signature,
  tests: TestInput[],
  timeoutMs: number,
  outFile: string,
  target = "Solution",
  file = "Solution.java",
): string {
  const blocks = tests
    .map((t, i) => {
      const args = t.args.map((a, k) => JAVA_TYPES[sig.params[k]](a)).join(", ");
      return `    vxRun(${i}, () -> ${target}.${fn}(${args}));`;
    })
    .join("\n");
  return `import java.io.*;
import java.util.*;

${JAVA_GUARD}

public class VxMain {
${javaWhere(file)}
  interface Call { Object call() throws Throwable; }
  static StringBuilder res = new StringBuilder();
  static PrintStream realOut = System.out;

${JAVA_QUOTE}

  static String j(Object o) {
    if (o == null) return "null";
    if (o instanceof String) return q((String) o);
    if (o instanceof Character) return q(String.valueOf(o));
    if (o instanceof Boolean || o instanceof Integer || o instanceof Long || o instanceof Short || o instanceof Byte) return o.toString();
    if (o instanceof Double || o instanceof Float) {
      double d = ((Number) o).doubleValue();
      return d == Math.rint(d) && Math.abs(d) < 1e15 ? String.valueOf((long) d) : String.valueOf(d);
    }
    if (o instanceof int[]) { List<Object> l = new ArrayList<>(); for (int x : (int[]) o) l.add(x); return j(l); }
    if (o instanceof long[]) { List<Object> l = new ArrayList<>(); for (long x : (long[]) o) l.add(x); return j(l); }
    if (o instanceof boolean[]) { List<Object> l = new ArrayList<>(); for (boolean x : (boolean[]) o) l.add(x); return j(l); }
    if (o instanceof Object[]) return j(Arrays.asList((Object[]) o));
    if (o instanceof Collection) {
      StringBuilder b = new StringBuilder("[");
      boolean first = true;
      for (Object x : (Collection<?>) o) { if (!first) b.append(','); first = false; b.append(j(x)); }
      return b.append(']').toString();
    }
    if (o instanceof Map) {
      StringBuilder b = new StringBuilder("{");
      boolean first = true;
      for (Map.Entry<?, ?> e : new TreeMap<Object, Object>((Map<?, ?>) o).entrySet()) {
        if (!first) b.append(','); first = false;
        b.append(q(String.valueOf(e.getKey()))).append(':').append(j(e.getValue()));
      }
      return b.append('}').toString();
    }
    return q(o.toString());
  }

  static boolean timedOut = false;
  static void vxRun(int i, Call c) {
    if (timedOut) {
      res.append("{\\"i\\":").append(i).append(",\\"output\\":null,\\"error\\":")
        .append(q("Skipped because an earlier test timed out.")).append(",\\"stdout\\":\\"\\",\\"ms\\":0}\\n");
      return;
    }
    ByteArrayOutputStream buf = new ByteArrayOutputStream();
    System.setOut(new PrintStream(buf, true));
    String output = null, error = null;
    long t0 = System.currentTimeMillis();
    VxGuard.deadline = t0 + ${timeoutMs};
    try {
      output = j(c.call());
    } catch (VxTimeout e) {
      timedOut = true;
      error = "This test took longer than ${Math.round(timeoutMs / 1000)} seconds, so I stopped it. Is there a loop that never ends?";
    } catch (StackOverflowError e) {
      error = "StackOverflowError: your method calls itself too many times. Is there a base case that stops the recursion?";
    } catch (Throwable e) {
      error = e.toString();
      error += vxWhere(e);
    }
    VxGuard.deadline = Long.MAX_VALUE;
    System.setOut(realOut);
    String out = buf.toString();
    if (out.length() > 4000) out = out.substring(0, 4000);
    res.append("{\\"i\\":").append(i)
      .append(",\\"output\\":").append(output == null ? "null" : q(output))
      .append(",\\"error\\":").append(error == null ? "null" : q(error))
      .append(",\\"stdout\\":").append(q(out))
      .append(",\\"ms\\":").append(System.currentTimeMillis() - t0).append("}\\n");
  }

  public static void main(String[] args) throws Exception {
${blocks}
    try (Writer w = new OutputStreamWriter(new FileOutputStream("${outFile}"), "UTF-8")) { w.write(res.toString()); }
  }
}
`;
}

/**
 * Runs the learner's main() with typed input on System.in and the output captured.
 * System.exit() is turned into a normal stop so the output isn't lost.
 */
export function javaProgram(mainClass: string, stdin: string, timeoutMs: number, outFile: string, file: string): string {
  return `import java.io.*;
import java.util.*;

${JAVA_GUARD}

class VxExit extends SecurityException {
  final int code;
  VxExit(int code) { this.code = code; }
}

public class VxProgram {
${JAVA_QUOTE}
${javaWhere(file)}

  public static void main(String[] args) throws Exception {
    ByteArrayOutputStream out = new ByteArrayOutputStream(), err = new ByteArrayOutputStream();
    PrintStream realOut = System.out, realErr = System.err;
    System.setIn(new ByteArrayInputStream(${JSON.stringify(stdin)}.getBytes("UTF-8")));
    System.setOut(new PrintStream(out, true, "UTF-8"));
    System.setErr(new PrintStream(err, true, "UTF-8"));
    try {
      System.setSecurityManager(new SecurityManager() {
        @Override public void checkExit(int status) { throw new VxExit(status); }
        @Override public void checkPermission(java.security.Permission p) {}
        @Override public void checkPermission(java.security.Permission p, Object ctx) {}
      });
    } catch (Throwable ignored) {}
    String error = null, kind = null;
    int exit = 0;
    VxGuard.deadline = System.currentTimeMillis() + ${timeoutMs};
    try {
      ${mainClass}.main(new String[0]);
    } catch (VxTimeout e) {
      kind = "timeout";
    } catch (VxExit e) {
      exit = e.code;
    } catch (StackOverflowError e) {
      kind = "runtime";
      error = "StackOverflowError: a method calls itself too many times. Is there a base case that stops the recursion?";
    } catch (NoSuchElementException e) {
      kind = "input";
      error = e.toString();
    } catch (Throwable e) {
      Throwable c = e;
      if (c instanceof ExceptionInInitializerError && c.getCause() != null) c = c.getCause();
      if (c instanceof VxExit) { exit = ((VxExit) c).code; }
      else {
        kind = "runtime";
        error = c.toString();
        error += vxWhere(c);
      }
    }
    VxGuard.deadline = Long.MAX_VALUE;
    System.out.flush();
    System.err.flush();
    System.setOut(realOut);
    System.setErr(realErr);
    String o = out.toString("UTF-8"), e2 = err.toString("UTF-8");
    if (o.length() > 20000) o = o.substring(0, 20000);
    if (e2.length() > 20000) e2 = e2.substring(0, 20000);
    String res = "{\\"stdout\\":" + q(o) + ",\\"stderr\\":" + q(e2) + ",\\"exit\\":" + exit
      + ",\\"kind\\":" + (kind == null ? "null" : q(kind)) + ",\\"error\\":" + (error == null ? "null" : q(error)) + "}";
    try (Writer w = new OutputStreamWriter(new FileOutputStream("${outFile}"), "UTF-8")) { w.write(res); }
  }
}
`;
}

export function javaCompileMessage(text: string, file = "Solution.java"): string {
  const own = new RegExp(`^\\/[^\\s:]*${file.replace(/[$.]/g, "\\$&")}:(\\d+):`);
  const lines = text.split("\n").filter((l) => l.trim() && !/^\d+ errors?$/.test(l.trim()));
  if (lines.length && !lines.some((l) => own.test(l)) && /Vx(Main|Program|Guard|Timeout|Exit)/.test(text)) {
    return "Something in your code clashes with the test runner. Please don't name a class VxMain, VxProgram or VxGuard.";
  }
  return (
    lines
      .map((l) => l.replace(/VxGuard\.tick\(\) && \(/g, "(").replace(/VxGuard\.tick\(\);/g, ""))
      .map((l) => l.replace(own, "Line $1:"))
      .map((l) => l.replace(/^\/[^\s:]*\/([\w$]+\.java):(\d+):/, "$1, line $2:"))
      .slice(0, 12)
      .join("\n") || "Your code didn't compile."
  );
}

// ---------- PHP ----------

/**
 * php-wasm has no STDIN or STDERR and its readline() blocks, so these are defined first, on the
 * same line as `<?php` so PHP's line numbers still match the learner's code.
 */
function phpShim(stdin: string): string {
  const b64 = typeof btoa === "function" ? btoa(unescape(encodeURIComponent(stdin))) : Buffer.from(stdin, "utf8").toString("base64");
  return (
    `if (!defined("STDIN")) { $__vx_in = fopen("php://memory", "r+"); fwrite($__vx_in, base64_decode("${b64}")); rewind($__vx_in); define("STDIN", $__vx_in); unset($__vx_in); } ` +
    `if (!defined("STDOUT")) define("STDOUT", fopen("php://output", "w")); ` +
    `if (!defined("STDERR")) define("STDERR", fopen("php://output", "w")); ` +
    `function __vx_readline($prompt = null) { if ($prompt !== null) echo $prompt; $l = fgets(STDIN); return $l === false ? false : rtrim($l, "\\r\\n"); } `
  );
}

/** The learner's code as a runnable script, with input available on STDIN. */
export function phpSource(code: string, stdin = ""): string {
  // php-wasm's own readline() waits for a keyboard that isn't there, so calls go to the shim instead.
  const body = code.replace(/\?>\s*$/, "").replace(/(?<![\w$>:\\])(?<!function\s+)readline(?=\s*\()/gi, "__vx_readline");
  const m = /^\s*<\?php\b/.exec(body);
  return m ? `${m[0]} ${phpShim(stdin)}${body.slice(m[0].length)}` : `<?php ${phpShim(stdin)}${body}`;
}

/** php-wasm calls the script "php-wasm run script"; say "line N" instead. */
export function phpTidy(text: string): string {
  return text
    .replace(/ in php-wasm run script on line (\d+)/g, " (line $1)")
    .replace(/ in php-wasm run script:(\d+)/g, " (line $1)")
    .replace(/^PHP (?=(Fatal|Parse|Warning|Notice|Deprecated))/gm, "");
}

export function phpProgram(code: string, fn: string, sig: Signature, tests: TestInput[]): string {
  const body = phpSource(code);
  const asMap = sig.returns === "map";
  const calls = tests
    .map((t, i) => {
      const args = JSON.stringify(t.args).replace(/\\/g, "\\\\").replace(/'/g, "\\'");
      return `vx_run(${i}, '${args}');`;
    })
    .join("\n");
  return `${body}
;
function vx_run($i, $args) {
  echo "\\x01VX|B|$i\\n";
  ob_start();
  try {
    if (!function_exists(${JSON.stringify(fn)})) throw new Error("I couldn't find a function called ${fn}. Keep its name exactly as in the starter code.");
    $r = ${fn}(...json_decode($args, true));
    $o = ob_get_clean();
    echo "\\x01VX|O|$i|" . json_encode($o) . "\\n";
    $r = ${asMap ? "is_array($r) ? (object)$r : $r" : "$r"};
    echo "\\x01VX|R|$i|" . json_encode($r, JSON_PRESERVE_ZERO_FRACTION) . "\\n";
  } catch (Throwable $e) {
    $o = ob_get_clean();
    echo "\\x01VX|O|$i|" . json_encode($o) . "\\n";
    echo "\\x01VX|E|$i|" . json_encode(get_class($e) . ": " . $e->getMessage() . ($e->getFile() === __FILE__ && $e->getLine() > ${body.split("\n").length} ? "" : " (line " . $e->getLine() . ")")) . "\\n";
  }
}
${calls}
`;
}

// ---------- Hints ----------

/** A line that calls the exercise function and prints the result, in the learner's language. */
export function exampleCall(language: string, fn: string, args: unknown[], sig?: Signature | null): string {
  const py = (v: unknown): string =>
    JSON.stringify(v).replace(/\btrue\b/g, "True").replace(/\bfalse\b/g, "False").replace(/\bnull\b/g, "None").replace(/,(?=\S)/g, ", ");
  const js = (v: unknown) => JSON.stringify(v).replace(/,(?=\S)/g, ", ");
  const php = (v: unknown): string =>
    Array.isArray(v) ? `[${v.map(php).join(", ")}]` : typeof v === "string" ? JSON.stringify(v).replace(/\$/g, "\\$") : js(v);
  const typed = (types: Record<string, (v: unknown) => string>, fallback: (v: unknown) => string) =>
    args.map((a, k) => (sig && types[sig.params[k]] ? types[sig.params[k]](a) : fallback(a))).join(", ");
  switch (language) {
    case "python":
      return `print(${fn}(${args.map(py).join(", ")}))`;
    case "javascript":
      return `console.log(${fn}(${args.map(js).join(", ")}));`;
    case "php":
      return `echo json_encode(${fn}(${args.map(php).join(", ")})), "\\n";`;
    case "cpp": {
      const call = `${fn}(${typed({ ...CPP_TYPES, "int[]": (v) => `{${(v as number[]).join(", ")}}` }, js)})`;
      const ret = sig?.returns ?? "";
      const body = ret.endsWith("[]")
        ? `    for (auto x : ${call}) cout << x << " ";\n    cout << endl;`
        : `    cout << ${call} << endl;`;
      return `int main() {\n${body}\n}`;
    }
    case "java": {
      const call = `Solution.${fn}(${typed(JAVA_TYPES, js)})`;
      const shown = (sig?.returns ?? "").endsWith("[]") ? `java.util.Arrays.toString(${call})` : call;
      return `public static void main(String[] args) {\n    System.out.println(${shown});\n}`;
    }
    default:
      return "";
  }
}
