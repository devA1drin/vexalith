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

export function cppProgram(code: string, fn: string, sig: Signature, tests: TestInput[]): string {
  const calls = tests
    .map((t, i) => {
      const args = t.args.map((a, k) => CPP_TYPES[sig.params[k]](a)).join(", ");
      return `  std::cout << "\\001VX|B|${i}" << std::endl;\n  { auto vx_r = ${fn}(${args}); std::cout << "\\n\\001VX|R|${i}|" << vx_::j(vx_r) << std::endl; }`;
    })
    .join("\n");
  return `${code}
#include <iostream>
#include <map>
#include <string>
#include <vector>
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

export function javaMain(fn: string, sig: Signature, tests: TestInput[], timeoutMs: number, outFile: string): string {
  const blocks = tests
    .map((t, i) => {
      const args = t.args.map((a, k) => JAVA_TYPES[sig.params[k]](a)).join(", ");
      return `    vxRun(${i}, () -> Solution.${fn}(${args}));`;
    })
    .join("\n");
  return `import java.io.*;
import java.util.*;

class VxTimeout extends RuntimeException {}

class VxGuard {
  static long deadline = Long.MAX_VALUE;
  static boolean tick() {
    if (System.currentTimeMillis() > deadline) throw new VxTimeout();
    return true;
  }
}

public class Main {
  interface Call { Object call() throws Throwable; }
  static StringBuilder res = new StringBuilder();
  static PrintStream realOut = System.out;

  static String q(String s) {
    StringBuilder b = new StringBuilder("\\"");
    for (char c : s.toCharArray()) {
      if (c == '"' || c == '\\\\') b.append('\\\\').append(c);
      else if (c == '\\n') b.append("\\\\n");
      else if (c < 0x20) b.append(String.format("\\\\u%04x", (int) c));
      else b.append(c);
    }
    return b.append('"').toString();
  }

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
      for (StackTraceElement f : e.getStackTrace()) {
        if ("Solution.java".equals(f.getFileName())) { error += " (line " + f.getLineNumber() + ")"; break; }
      }
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

export function javaCompileMessage(text: string): string {
  if (/class Main|Main\.java/.test(text) && !/Solution\.java/.test(text)) {
    return "Something in your code clashes with the test runner. Keep your code inside class Solution and don't add a class named Main.";
  }
  return (
    text
      .replace(/VxGuard\.tick\(\) && \(/g, "(")
      .split("\n")
      .filter((l) => l.trim() && !/^\d+ errors?$/.test(l.trim()))
      .map((l) => l.replace(/^\/[^\s:]*Solution\.java:(\d+):/, "Line $1:"))
      .slice(0, 12)
      .join("\n") || "Your code didn't compile."
  );
}

// ---------- PHP ----------

export function phpProgram(code: string, fn: string, sig: Signature, tests: TestInput[]): string {
  let body = code.replace(/\?>\s*$/, "");
  if (!/^\s*<\?php/.test(body)) body = "<?php\n" + body;
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
    $r = ${fn}(...json_decode($args, true));
    $o = ob_get_clean();
    echo "\\x01VX|O|$i|" . json_encode($o) . "\\n";
    $r = ${asMap ? "is_array($r) ? (object)$r : $r" : "$r"};
    echo "\\x01VX|R|$i|" . json_encode($r, JSON_PRESERVE_ZERO_FRACTION) . "\\n";
  } catch (Throwable $e) {
    $o = ob_get_clean();
    echo "\\x01VX|O|$i|" . json_encode($o) . "\\n";
    echo "\\x01VX|E|$i|" . json_encode(get_class($e) . ": " . $e->getMessage() . " (line " . $e->getLine() . ")") . "\\n";
  }
}
${calls}
`;
}
