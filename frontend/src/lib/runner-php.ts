/**
 * PHP in the browser with php-wasm (Apache-2.0, PHP compiled to WebAssembly),
 * loaded from the jsDelivr CDN the first time PHP is used.
 * Every run gets a fresh Web Worker: PHP loads, then network and storage APIs
 * are removed before the learner's code starts. A timer terminates the worker
 * if a test hangs.
 */
import { parseMarked, phpProgram } from "./harness";
import { LOCKDOWN_JS, makeWorker, markerWatcher, timeoutMessage, type RunResult, type Signature, type TestInput } from "./runner";

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
    await php.run(ev.data.source);
    self.postMessage({ done: true });
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
      const problem = extra.trim() ? extra.trim().replace(/^PHP /gm, "").slice(0, 800) : "";
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
