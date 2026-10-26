/**
 * Runs learner code in the learner's own browser. Nothing is executed on a server.
 *
 * - JavaScript: a dedicated Web Worker built from a Blob. Before the learner's code
 *   runs, the worker removes network and storage APIs (fetch, XHR, WebSocket,
 *   importScripts, IndexedDB, ...). Workers have no DOM, cookies or page access.
 * - Python: Pyodide (CPython compiled to WebAssembly) loaded from the jsDelivr CDN
 *   into its own Web Worker; the same APIs are removed once Pyodide has loaded.
 *
 * - C++, Java, PHP: see runner-cpp.ts, runner-java.ts and runner-php.ts. Each is
 *   loaded only when that language is used.
 *
 * Every test has a time limit. If the code is still busy when it runs out (say,
 * an infinite loop), the worker is terminated, so the page never freezes.
 */

export type RunLanguage = "python" | "javascript" | "cpp" | "java" | "php";
export type Signature = { params: string[]; returns: string };
export type RunOptions = {
  language: RunLanguage;
  code: string;
  fn: string;
  tests: TestInput[];
  timeoutMs: number;
  signature?: Signature | null;
  onStatus?: (s: string) => void;
};
export type TestInput = { args: unknown[] };
export type RunResult = { output: string | null; error: string | null; stdout: string; ms: number };

/** What went wrong in "Run my code", in a form the Output panel can explain. */
export type ProblemKind = "compile" | "runtime" | "timeout" | "input" | "missing" | "load";
export type ProgramResult = {
  stdout: string;
  stderr: string;
  problem: { kind: ProblemKind; message: string } | null;
  exitCode: number;
  ms: number;
  truncated: boolean;
};

/** "Run my code" stops a program after this long. */
export const PROGRAM_TIMEOUT_MS = 10_000;
/** At most this many characters of output are kept per stream. */
export const OUTPUT_LIMIT = 20_000;

export function programTimeoutMessage(ms = PROGRAM_TIMEOUT_MS): string {
  return `Your program was still running after ${Math.round(ms / 1000)} seconds, so I stopped it. Is there a loop that never ends, or is it waiting for more input?`;
}

/** Collects streamed output, keeping each stream under OUTPUT_LIMIT. */
export function outputCollector() {
  const c = { stdout: "", stderr: "", truncated: false };
  return {
    push(stream: "out" | "err", text: string) {
      const key = stream === "err" ? "stderr" : "stdout";
      const room = OUTPUT_LIMIT - c[key].length;
      if (room <= 0) {
        c.truncated = true;
        return;
      }
      if (text.length > room) c.truncated = true;
      c[key] += text.slice(0, room);
    },
    get value() {
      return c;
    },
  };
}

export const PYODIDE_VERSION = "0.29.5";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

const LOCKDOWN = `
for (const k of ["fetch","XMLHttpRequest","WebSocket","EventSource","importScripts","indexedDB","caches","BroadcastChannel","Worker","SharedWorker","WebTransport","RTCPeerConnection"]) {
  try { Object.defineProperty(self, k, { value: undefined, writable: false, configurable: false }); } catch (e) {}
}
try { Object.defineProperty(navigator, "sendBeacon", { value: undefined }); } catch (e) {}
`;

const JS_WORKER = `
${LOCKDOWN}
self.onmessage = (ev) => {
  const { code, fn, tests } = ev.data;
  let out = "";
  const log = (...a) => { if (out.length < 4000) out += a.map((x) => typeof x === "string" ? x : (() => { try { return JSON.stringify(x); } catch { return String(x); } })()).join(" ") + "\\n"; };
  self.console = { log, info: log, warn: log, error: log, debug: log };
  let f;
  self.postMessage({ start: 0 });
  try {
    f = new Function(code + "\\n;return typeof " + fn + " === 'function' ? " + fn + " : undefined;")();
  } catch (e) {
    for (let i = 0; i < tests.length; i++) self.postMessage({ i, output: null, error: String(e && e.name ? e.name + ": " + e.message : e), stdout: out, ms: 0 });
    self.postMessage({ done: true });
    return;
  }
  for (let i = 0; i < tests.length; i++) {
    if (i > 0) out = ""; // anything printed at the top level shows with the first test
    const t0 = performance.now();
    self.postMessage({ start: i });
    try {
      if (!f) throw new Error("I couldn't find a function called " + fn + ". Keep its name exactly as in the starter code.");
      const r = f(...structuredClone(tests[i].args));
      const s = JSON.stringify(r);
      self.postMessage({ i, output: s === undefined ? null : s, error: s === undefined ? "Your function returned undefined. Did you forget the return statement?" : null, stdout: out, ms: performance.now() - t0 });
    } catch (e) {
      self.postMessage({ i, output: null, error: e && e.name ? e.name + ": " + e.message : String(e), stdout: out, ms: performance.now() - t0 });
    }
  }
  self.postMessage({ done: true });
};
`;

const PY_HARNESS = `
import json, sys, io, traceback
def __vx_run(code, fn, args_json):
    buf = io.StringIO()
    old = sys.stdout, sys.stdin
    sys.stdout = buf
    sys.stdin = io.StringIO("")
    try:
        ns = {"__name__": "__vexalith__"}
        exec(code, ns)
        f = ns.get(fn)
        if not callable(f):
            raise NameError(f"I couldn't find a function called {fn}. Keep its name exactly as in the starter code.")
        result = f(*json.loads(args_json))
        try:
            return json.dumps({"output": json.dumps(result), "error": None, "stdout": buf.getvalue()[:4000]})
        except TypeError:
            return json.dumps({"output": None, "error": f"Your function returned {type(result).__name__}, which can't be compared. Return a number, text, True/False, a list or a dict.", "stdout": buf.getvalue()[:4000]})
    except EOFError as e:
        msg = "The tests call your function directly, so input() has nothing to read. Use the function's parameters instead." + __vx_where(e)
        return json.dumps({"output": None, "error": msg, "stdout": buf.getvalue()[:4000]})
    except BaseException as e:
        return json.dumps({"output": None, "error": f"{type(e).__name__}: {e}" + __vx_where(e), "stdout": buf.getvalue()[:4000]})
    finally:
        sys.stdout, sys.stdin = old

def __vx_where(e):
    if isinstance(e, SyntaxError) and e.filename == "<string>" and e.lineno:
        return f" (line {e.lineno})"
    tb = traceback.extract_tb(e.__traceback__)
    line = next((fr.lineno for fr in reversed(tb) if fr.filename == "<string>"), None)
    return f" (line {line})" if line else ""

class __VxStream(io.TextIOBase):
    def __init__(self, kind):
        self.kind = kind
    def writable(self):
        return True
    def write(self, s):
        if s:
            _vx_emit(self.kind, s)
        return len(s)

def __vx_program(code, stdin):
    old = sys.stdout, sys.stderr, sys.stdin
    sys.stdout, sys.stderr, sys.stdin = __VxStream("out"), __VxStream("err"), io.StringIO(stdin)
    kind = error = None
    exit_code = 0
    try:
        exec(compile(code, "<string>", "exec"), {"__name__": "__main__"})
    except SystemExit as e:
        if isinstance(e.code, int):
            exit_code = e.code
        elif e.code is not None:
            sys.stderr.write(str(e.code) + "\\n")
            exit_code = 1
    except SyntaxError as e:
        kind, error = "compile", f"{type(e).__name__}: {e.msg}" + __vx_where(e)
    except EOFError as e:
        kind, error = "input", "EOFError: input() found no more lines to read" + __vx_where(e)
    except RecursionError as e:
        kind, error = "runtime", "RecursionError: a function calls itself too many times. Is there a base case that stops it?" + __vx_where(e)
    except BaseException as e:
        kind, error = "runtime", f"{type(e).__name__}: {e}" + __vx_where(e)
    finally:
        sys.stdout, sys.stderr, sys.stdin = old
    return json.dumps({"kind": kind, "error": error, "exit": exit_code})
`;

const PY_WORKER = `
importScripts("${PYODIDE_URL}pyodide.js");
let py = null;
let room = ${OUTPUT_LIMIT * 2};
self.vxEmit = (kind, text) => {
  if (room <= 0) return;
  room -= text.length;
  self.postMessage({ chunk: text, stream: kind });
};
const ready = (async () => {
  py = await loadPyodide({ indexURL: "${PYODIDE_URL}" });
  py.runPython("from js import vxEmit as _vx_emit\\n" + ${JSON.stringify(PY_HARNESS)});
  ${LOCKDOWN}
  self.postMessage({ ready: true });
})().catch((e) => self.postMessage({ loadError: String(e) }));
self.onmessage = async (ev) => {
  await ready;
  if (ev.data.program) {
    room = ${OUTPUT_LIMIT * 2};
    self.postMessage({ start: 0 });
    const t0 = performance.now();
    const r = JSON.parse(py.globals.get("__vx_program")(ev.data.code, ev.data.stdin));
    self.postMessage({ program: r, ms: performance.now() - t0 });
    return;
  }
  const { code, fn, tests } = ev.data;
  const run = py.globals.get("__vx_run");
  for (let i = 0; i < tests.length; i++) {
    self.postMessage({ start: i });
    const t0 = performance.now();
    const r = JSON.parse(run(code, fn, JSON.stringify(tests[i].args)));
    self.postMessage({ i, ...r, ms: performance.now() - t0 });
  }
  self.postMessage({ done: true });
};
`;

export const LOCKDOWN_JS = LOCKDOWN;

export function makeWorker(src: string, module = false): Worker {
  const url = URL.createObjectURL(new Blob([src], { type: "text/javascript" }));
  const w = new Worker(url, module ? { type: "module" } : undefined);
  URL.revokeObjectURL(url);
  return w;
}

// Pyodide takes a few seconds to load, so its worker is kept between runs (until a timeout kills it).
let pyWorker: Worker | null = null;
let pyReady: Promise<void> | null = null;

export function preparePython(onStatus?: (s: string) => void): Promise<void> {
  if (pyWorker && pyReady) return pyReady;
  onStatus?.("Downloading Python (about 5 MB, only the first time)…");
  const w = makeWorker(PY_WORKER);
  pyWorker = w;
  pyReady = new Promise<void>((resolve, reject) => {
    const onMsg = (ev: MessageEvent) => {
      if (ev.data?.ready) {
        w.removeEventListener("message", onMsg);
        resolve();
      } else if (ev.data?.loadError) {
        w.removeEventListener("message", onMsg);
        killPython();
        reject(new Error("Python couldn't load. Check your internet connection and try again."));
      }
    };
    w.addEventListener("message", onMsg);
  });
  return pyReady;
}

function killPython() {
  pyWorker?.terminate();
  pyWorker = null;
  pyReady = null;
}

export type ProgramOptions = {
  language: RunLanguage;
  code: string;
  /** Text the program can read (input(), prompt(), cin, Scanner, fgets(STDIN)). */
  stdin: string;
  onStatus?: (s: string) => void;
};

/** "Run my code": run the learner's code as a program and collect what it prints. */
export async function runProgram(opts: ProgramOptions): Promise<ProgramResult> {
  const { language, code, stdin, onStatus } = opts;
  if (language === "cpp" || language === "java" || language === "php") {
    const mod =
      language === "cpp" ? await import("./runner-cpp") : language === "java" ? await import("./runner-java") : await import("./runner-php");
    return mod.runProgram(code, stdin, PROGRAM_TIMEOUT_MS, onStatus);
  }
  return language === "python" ? runPythonProgram(code, stdin, onStatus) : runJsProgram(code, stdin, onStatus);
}

export function programFailure(kind: ProblemKind, message: string): ProgramResult {
  return { stdout: "", stderr: "", problem: { kind, message }, exitCode: 0, ms: 0, truncated: false };
}

async function runPythonProgram(code: string, stdin: string, onStatus?: (s: string) => void): Promise<ProgramResult> {
  try {
    await preparePython(onStatus);
  } catch (e) {
    return programFailure("load", e instanceof Error ? e.message : "Python couldn't load.");
  }
  onStatus?.("Running your code…");
  const w = pyWorker as Worker;
  const col = outputCollector();
  return new Promise<ProgramResult>((resolve) => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const t0 = performance.now();
    const done = (problem: ProgramResult["problem"], exitCode = 0, ms?: number) => {
      clearTimeout(timer);
      w.removeEventListener("message", onMsg);
      resolve({ ...col.value, problem, exitCode, ms: ms ?? performance.now() - t0 });
    };
    const onMsg = (ev: MessageEvent) => {
      const d = ev.data;
      if (typeof d?.chunk === "string") col.push(d.stream === "err" ? "err" : "out", d.chunk);
      else if (typeof d?.start === "number") {
        timer = setTimeout(() => {
          killPython();
          done({ kind: "timeout", message: programTimeoutMessage() }, 0, PROGRAM_TIMEOUT_MS);
        }, PROGRAM_TIMEOUT_MS);
      } else if (d?.program) {
        const r = d.program;
        done(r.error ? { kind: r.kind ?? "runtime", message: r.error } : null, r.exit ?? 0, d.ms);
      }
    };
    w.addEventListener("message", onMsg);
    w.postMessage({ program: true, code, stdin });
  });
}

/**
 * The JavaScript program runs as the worker's own script, so a syntax error comes
 * back with its line number. This prelude goes first: it locks the worker down,
 * captures console output, gives prompt() the typed input, and keeps track of
 * timers so the run ends when nothing is left to do.
 */
function jsProgramPrelude(stdin: string): string {
  const lines = stdin === "" ? [] : stdin.replace(/\r/g, "").replace(/\n$/, "").split("\n");
  return `(() => {
${LOCKDOWN}
const input = ${JSON.stringify(lines)};
let sent = 0;
const post = (stream, text) => { if (sent > ${OUTPUT_LIMIT * 2}) return; sent += text.length; postMessage({ chunk: text, stream }); };
const fmt = (v, depth, seen) => {
  if (typeof v === "string") return depth ? JSON.stringify(v) : v;
  if (typeof v === "function") return "[Function" + (v.name ? ": " + v.name : " (anonymous)") + "]";
  if (typeof v === "bigint") return v + "n";
  if (typeof v === "symbol") return v.toString();
  if (v === null || typeof v !== "object") return String(v);
  if (v instanceof Error) return v.name + ": " + v.message;
  if (seen.has(v)) return "[Circular]";
  if (depth > 4) return Array.isArray(v) ? "[Array]" : "[Object]";
  seen.add(v);
  let s;
  if (Array.isArray(v)) s = "[" + v.map((x) => fmt(x, depth + 1, seen)).join(", ") + "]";
  else if (v instanceof Map) s = "Map(" + v.size + ") {" + [...v].map(([k, x]) => " " + fmt(k, depth + 1, seen) + " => " + fmt(x, depth + 1, seen)).join(",") + (v.size ? " " : "") + "}";
  else if (v instanceof Set) s = "Set(" + v.size + ") {" + [...v].map((x) => " " + fmt(x, depth + 1, seen)).join(",") + (v.size ? " " : "") + "}";
  else {
    const keys = Object.keys(v);
    const name = v.constructor && v.constructor !== Object && v.constructor.name ? v.constructor.name + " " : "";
    s = name + "{" + keys.map((k) => " " + (/^[A-Za-z_$][\\w$]*$/.test(k) ? k : JSON.stringify(k)) + ": " + fmt(v[k], depth + 1, seen)).join(",") + (keys.length ? " " : "") + "}";
  }
  seen.delete(v);
  return s;
};
const line = (a) => a.map((x) => fmt(x, 0, new Set())).join(" ") + "\\n";
const out = (...a) => post("out", line(a));
const err = (...a) => post("err", line(a));
self.console = { log: out, info: out, debug: out, trace: out, dir: out, table: out, group: out, groupCollapsed: out, groupEnd() {}, time() {}, timeEnd() {}, count() {}, warn: err, error: err, assert: (ok, ...a) => { if (!ok) err("Assertion failed:", ...a); } };
self.prompt = (msg) => { if (msg !== undefined) post("out", String(msg)); return input.length ? input.shift() : null; };
self.alert = (msg) => out(msg === undefined ? "" : msg);
const pending = new Set();
let mainDone = false;
const st = setTimeout, ct = clearTimeout, si = setInterval, ci = clearInterval;
const check = () => { if (mainDone && pending.size === 0) st(() => { if (pending.size === 0) postMessage({ done: true }); }, 0); };
self.setTimeout = (f, ms, ...a) => { const id = st(() => { pending.delete(id); try { if (typeof f === "function") f(...a); } finally { check(); } }, ms); pending.add(id); return id; };
self.clearTimeout = (id) => { if (pending.delete(id)) { ct(id); check(); } };
self.setInterval = (f, ms, ...a) => { const id = si(() => { if (typeof f === "function") f(...a); }, ms); pending.add(id); return id; };
self.clearInterval = (id) => { if (pending.delete(id)) { ci(id); check(); } };
self.__vxDone = () => { mainDone = true; check(); };
self.addEventListener("error", (e) => { e.preventDefault(); postMessage({ uncaught: String(e.message || e.error), line: e.lineno }); });
self.addEventListener("unhandledrejection", (e) => { e.preventDefault(); const r = e.reason; postMessage({ uncaught: r && r.name ? r.name + ": " + r.message : "Uncaught (in promise) " + String(r), line: 0, stack: r && r.stack ? String(r.stack) : "" }); });
})();`;
}

/** Turn a worker script line into the learner's line (0 when it isn't in their code). */
function jsLine(line: number, offset: number, codeLines: number): number {
  const l = line - offset;
  return l >= 1 && l <= codeLines ? l : 0;
}

function runJsProgram(code: string, stdin: string, onStatus?: (s: string) => void): Promise<ProgramResult> {
  onStatus?.("Running your code…");
  const prelude = jsProgramPrelude(stdin);
  const offset = prelude.split("\n").length;
  const codeLines = code.split("\n").length;
  const worker = makeWorker(`${prelude}\n${code}\n;self.__vxDone();\n`);
  const col = outputCollector();
  const t0 = performance.now();
  return new Promise<ProgramResult>((resolve) => {
    const done = (problem: ProgramResult["problem"]) => {
      clearTimeout(timer);
      worker.terminate();
      resolve({ ...col.value, problem, exitCode: 0, ms: performance.now() - t0 });
    };
    const timer = setTimeout(() => done({ kind: "timeout", message: programTimeoutMessage() }), PROGRAM_TIMEOUT_MS);
    const where = (line: number, stack = "") => {
      let l = jsLine(line, offset, codeLines);
      if (!l) {
        const m = /:(\d+):\d+\)?\s*$/m.exec(stack.split("\n").find((s) => /blob:|<anonymous>/.test(s)) ?? "");
        if (m) l = jsLine(Number(m[1]), offset, codeLines);
      }
      return l ? ` (line ${l})` : "";
    };
    worker.onmessage = (ev) => {
      const d = ev.data;
      if (typeof d?.chunk === "string") col.push(d.stream === "err" ? "err" : "out", d.chunk);
      else if (d?.done) done(null);
      else if (d?.uncaught) {
        const msg = String(d.uncaught).replace(/^Uncaught /, "");
        done({ kind: "runtime", message: msg + where(d.line ?? 0, d.stack) });
      }
    };
    // A syntax error stops the script before it starts; the browser reports it here.
    worker.onerror = (ev) => {
      ev.preventDefault();
      const msg = String(ev.message || "SyntaxError").replace(/^Uncaught /, "");
      done({ kind: /SyntaxError/.test(msg) ? "compile" : "runtime", message: msg + where(ev.lineno) });
    };
  });
}

export async function runTests(opts: RunOptions): Promise<RunResult[]> {
  const { language, code, fn, tests, timeoutMs, signature, onStatus } = opts;
  if (language === "cpp" || language === "java" || language === "php") {
    if (!signature) throw new Error("This exercise is missing its type information.");
    const mod =
      language === "cpp" ? await import("./runner-cpp") : language === "java" ? await import("./runner-java") : await import("./runner-php");
    return mod.run(code, fn, signature, tests, timeoutMs, onStatus);
  }
  return runScript(language, code, fn, tests, timeoutMs, onStatus);
}

async function runScript(
  language: "python" | "javascript",
  code: string,
  fn: string,
  tests: TestInput[],
  timeoutMs: number,
  onStatus?: (s: string) => void,
): Promise<RunResult[]> {
  let worker: Worker;
  if (language === "python") {
    await preparePython(onStatus);
    worker = pyWorker as Worker;
  } else {
    worker = makeWorker(JS_WORKER);
  }
  onStatus?.("Running tests…");
  const results: RunResult[] = tests.map(() => ({ output: null, error: "Didn't run", stdout: "", ms: 0 }));
  return new Promise<RunResult[]>((resolve) => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const finish = () => {
      clearTimeout(timer);
      worker.removeEventListener("message", onMsg);
      if (language === "javascript") worker.terminate();
      resolve(results);
    };
    const arm = (i: number) => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        // Still busy: most likely an infinite loop. Kill the worker so the page stays responsive.
        results[i] = {
          output: null,
          error: timeoutMessage(timeoutMs),
          stdout: "",
          ms: timeoutMs,
        };
        for (let j = i + 1; j < results.length; j++) results[j] = { ...results[j], error: "Skipped because an earlier test timed out." };
        worker.terminate();
        if (language === "python") killPython();
        clearTimeout(timer);
        resolve(results);
      }, timeoutMs);
    };
    const onMsg = (ev: MessageEvent) => {
      const d = ev.data;
      if (typeof d?.start === "number") arm(d.start);
      else if (typeof d?.i === "number") results[d.i] = { output: d.output ?? null, error: d.error ?? null, stdout: d.stdout ?? "", ms: d.ms ?? 0 };
      else if (d?.done) finish();
    };
    worker.addEventListener("message", onMsg);
    worker.postMessage({ code, fn, tests });
  });
}

/** Compare a reported JSON output with an expected value (key order doesn't matter). */
export function sameValue(output: string | null, expected: unknown): boolean {
  if (output === null) return false;
  try {
    return canonical(JSON.parse(output)) === canonical(expected);
  } catch {
    return false;
  }
}

function canonical(v: unknown): string {
  if (typeof v === "number" && Number.isInteger(v)) return String(v); // 3.0 and 3 are the same answer
  if (Array.isArray(v)) return `[${v.map(canonical).join(",")}]`;
  if (v && typeof v === "object") {
    return `{${Object.keys(v as object).sort().map((k) => `${JSON.stringify(k)}:${canonical((v as Record<string, unknown>)[k])}`).join(",")}}`;
  }
  return JSON.stringify(v);
}

/** Show a value the way the learner's language writes it (None/True in Python, null/true in JS). */
export function show(v: unknown, language: RunLanguage): string {
  const s = JSON.stringify(v);
  if (s === undefined) return "undefined";
  const spaced = s.replace(/":/g, '": ').replace(/,(?=\S)/g, ", ");
  if (language !== "python") return spaced;
  return spaced.replace(/\btrue\b/g, "True").replace(/\bfalse\b/g, "False").replace(/\bnull\b/g, "None");
}

/** Like show(), for an output string reported by the runner (keeps big integers exact). */
export function showOutput(output: string, language: RunLanguage): string {
  try {
    const v = JSON.parse(output);
    if (typeof v === "number" && !Number.isSafeInteger(v) && /^-?\d+$/.test(output)) return output;
    return show(v, language);
  } catch {
    return output;
  }
}

/**
 * Watches a stream of marked output and fires onStart(i) when test i begins,
 * so each test gets its own time limit.
 */
export function markerWatcher(onStart: (i: number) => void) {
  let text = "";
  let seen = -1;
  return {
    push(chunk: string) {
      text += chunk;
      const re = /\u0001VX\|B\|(\d+)/g;
      let m: RegExpExecArray | null;
      while ((m = re.exec(text))) {
        const i = Number(m[1]);
        if (i > seen) {
          seen = i;
          onStart(i);
        }
      }
    },
    get text() {
      return text;
    },
    get current() {
      return seen;
    },
  };
}

export function timeoutMessage(timeoutMs: number): string {
  return `This test took longer than ${Math.round(timeoutMs / 1000)} seconds, so I stopped it. Is there a loop that never ends?`;
}
