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
    out = "";
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
    old = sys.stdout
    sys.stdout = buf
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
    except BaseException as e:
        tb = traceback.extract_tb(e.__traceback__)
        line = next((fr.lineno for fr in reversed(tb) if fr.filename == "<string>"), None)
        msg = f"{type(e).__name__}: {e}" + (f" (line {line})" if line else "")
        return json.dumps({"output": None, "error": msg, "stdout": buf.getvalue()[:4000]})
    finally:
        sys.stdout = old
`;

const PY_WORKER = `
importScripts("${PYODIDE_URL}pyodide.js");
let py = null;
const ready = (async () => {
  py = await loadPyodide({ indexURL: "${PYODIDE_URL}" });
  py.runPython(${JSON.stringify(PY_HARNESS)});
  ${LOCKDOWN}
  self.postMessage({ ready: true });
})().catch((e) => self.postMessage({ loadError: String(e) }));
self.onmessage = async (ev) => {
  await ready;
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
