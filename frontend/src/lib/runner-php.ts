/**
 * PHP in the browser with php-wasm (Apache-2.0, PHP compiled to WebAssembly),
 * loaded from the jsDelivr CDN the first time PHP is used.
 * Every run gets a fresh Web Worker: PHP loads, then network and storage APIs
 * are removed before the learner's code starts. A timer terminates the worker
 * if a test hangs.
 */
import { parseMarked, phpProgram, phpSource, phpTidy } from "./harness";
import {
  LOCKDOWN_JS,
  makeWorker,
  markerWatcher,
  OUTPUT_LIMIT,
  programTimeoutMessage,
  timeoutMessage,
  type ProgramResult,
  type RunResult,
  type Signature,
  type TestInput,
} from "./runner";

export const PHP_WASM_VERSION = "0.2.0";
const PHP_URL = `https://cdn.jsdelivr.net/npm/php-wasm@${PHP_WASM_VERSION}/PhpWeb.mjs`;

const WORKER = `
// php-wasm's web build looks for these at start-up; a worker has no page, so give it stand-ins.
self.document = { addEventListener() {}, querySelector() { return null; }, body: null };
self.window = self;
self.onmessage = async (ev) => {
  try {
    const { PhpWeb } = await import(${JSON.stringify(PHP_URL)});
    const php = new PhpWeb();
    php.addEventListener("output", (e) => self.postMessage({ chunk: String(e.detail) }));
    php.addEventListener("error", (e) => self.postMessage({ chunk: String(e.detail) }));
    await php.binary;
    ${LOCKDOWN_JS}
    self.postMessage({ ready: true });
    const code = await php.run(ev.data.source);
    self.postMessage({ done: true, code: Number(code) || 0 });
  } catch (e) {
    self.postMessage({ done: true, failed: String(e && e.message || e) });
  }
};
`;

let loadedOnce = false;

export async function run(
  code: string,
  fn: string,
  sig: Signature,
  tests: TestInput[],
  timeoutMs: number,
  onStatus?: (s: string) => void,
): Promise<RunResult[]> {
  onStatus?.(loadedOnce ? "Starting PHP…" : "Downloading PHP (about 3 MB, only the first time)…");
  const worker = makeWorker(WORKER, true);
  return new Promise<RunResult[]>((resolve) => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let ready = false;
    const finish = (extraError?: string) => {
      clearTimeout(timer);
      worker.terminate();
      const { results, extra } = parseMarked(watch.text, tests.length);
      // Text outside the tests is either a PHP error or something the code printed at the top level.
      const split = splitPhpOutput(extra);
      const problem = [split.fatal, split.stderr.trim()].filter(Boolean).join("\n").slice(0, 800);
      if (split.stdout.trim() && results.length) results[0] = { ...results[0], stdout: split.stdout.trim() + "\n" + results[0].stdout };
      if (watch.current < 0) {
        const msg = extraError || (problem ? `PHP couldn't run your code:\n${problem}` : "PHP couldn't run your code.");
        return resolve(tests.map(() => ({ output: null, error: msg, stdout: "", ms: 0 })));
      }
      const cur = watch.current;
      if (cur < tests.length && (extraError || (results[cur].error && problem))) {
        results[cur] = { ...results[cur], output: null, error: extraError || `${results[cur].error}\n${problem}` };
        for (let j = cur + 1; j < tests.length; j++) results[j] = { ...results[j], error: "Skipped because an earlier test stopped the program." };
      }
      resolve(results);
    };
    const arm = () => {
      clearTimeout(timer);
      timer = setTimeout(() => finish(ready ? timeoutMessage(timeoutMs) : "PHP took too long to load. Check your connection and try again."), ready ? timeoutMs : 120_000);
    };
    const watch = markerWatcher(arm);
    arm();
    worker.onmessage = (ev) => {
      const d = ev.data;
      if (d.ready) {
        ready = loadedOnce = true;
        onStatus?.("Running tests…");
        arm();
      } else if (typeof d.chunk === "string") watch.push(d.chunk.endsWith("\n") ? d.chunk : d.chunk + "\n");
      else if (d.done) finish(d.failed ? `PHP couldn't start: ${d.failed}` : undefined);
    };
    worker.postMessage({ source: phpProgram(code, fn, sig, tests) });
  });
}

/**
 * Split what PHP printed into the program's output, warnings, and the error that
 * stopped it (php-wasm sends all of them on one stream).
 */
export function splitPhpOutput(text: string): { stdout: string; stderr: string; fatal: string | null } {
  const out: string[] = [];
  const warn: string[] = [];
  let fatal: string | null = null;
  let skipTrace = false;
  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    const m = /^(?:PHP )?(Fatal error|Parse error|Warning|Notice|Deprecated): (.*)$/.exec(l);
    if (m) {
      // PHP starts each message on a fresh line; drop the empty line that leaves behind.
      if (out.length && out[out.length - 1] === "") out.pop();
      const msg = phpTidy(`${m[1]}: ${m[2]}`).replace(/^Fatal error: Uncaught /, "");
      if (m[1] === "Fatal error" || m[1] === "Parse error") {
        fatal = fatal ?? msg;
        skipTrace = true;
      } else warn.push(msg);
      continue;
    }
    if (skipTrace && (/^Stack trace:/.test(l) || /^#\d+ /.test(l) || /^\s+thrown in /.test(l))) continue;
    skipTrace = false;
    out.push(l);
  }
  return { stdout: out.join("\n"), stderr: warn.length ? warn.join("\n") + "\n" : "", fatal };
}

/** "Run my code": run the learner's script as it is. */
export async function runProgram(code: string, stdin: string, timeoutMs: number, onStatus?: (s: string) => void): Promise<ProgramResult> {
  onStatus?.(loadedOnce ? "Starting PHP…" : "Downloading PHP (about 3 MB, only the first time)…");
  const worker = makeWorker(WORKER, true);
  let text = "";
  let t0 = performance.now();
  return new Promise<ProgramResult>((resolve) => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let ready = false;
    const done = (problem: ProgramResult["problem"], exitCode = 0) => {
      clearTimeout(timer);
      worker.terminate();
      const split = splitPhpOutput(text);
      const truncated = split.stdout.length > OUTPUT_LIMIT || split.stderr.length > OUTPUT_LIMIT;
      const fatal = split.fatal ? { kind: /^Parse error/.test(split.fatal) ? ("compile" as const) : ("runtime" as const), message: split.fatal } : null;
      resolve({
        stdout: split.stdout.slice(0, OUTPUT_LIMIT),
        stderr: split.stderr.slice(0, OUTPUT_LIMIT),
        problem: problem ?? fatal,
        exitCode: fatal ? 0 : exitCode,
        ms: performance.now() - t0,
        truncated,
      });
    };
    timer = setTimeout(() => done({ kind: "load", message: "PHP took too long to load. Check your connection and try again." }), 120_000);
    worker.onmessage = (ev) => {
      const d = ev.data;
      if (d.ready) {
        ready = loadedOnce = true;
        onStatus?.("Running your code…");
        t0 = performance.now();
        clearTimeout(timer);
        timer = setTimeout(() => done({ kind: "timeout", message: programTimeoutMessage(timeoutMs) }), timeoutMs);
      } else if (typeof d.chunk === "string") {
        if (text.length < OUTPUT_LIMIT * 2) text += d.chunk;
      } else if (d.done) {
        done(d.failed ? { kind: ready ? "runtime" : "load", message: `PHP couldn't start: ${d.failed}` } : null, d.code || 0);
      }
    };
    worker.postMessage({ source: phpSource(code, stdin) });
  });
}
