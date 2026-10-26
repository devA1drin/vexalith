/**
 * C++ in the browser, in two steps, each in its own Web Worker:
 * 1. Compile: Clang/LLD built for WebAssembly (YoWASP, Apache-2.0 / ISC), loaded
 *    from the jsDelivr CDN the first time C++ is used (~23 MB download, then cached).
 * 2. Run: the compiled program is WebAssembly. It can only call the handful of
 *    functions we give it (write text, read the clock, exit), so it has no way to
 *    reach the network, files or the page. A timer terminates it if it hangs.
 */
import { cppCompileMessage, cppProgram, cppSource, hasCppMain, parseMarked } from "./harness";
import {
  makeWorker,
  markerWatcher,
  outputCollector,
  programFailure,
  programTimeoutMessage,
  timeoutMessage,
  type ProgramResult,
  type RunResult,
  type Signature,
  type TestInput,
} from "./runner";

export const YOWASP_CLANG_VERSION = "22.0.0-git20542-10";
const CLANG_URL = `https://cdn.jsdelivr.net/npm/@yowasp/clang@${YOWASP_CLANG_VERSION}/gen/bundle.js`;

const COMPILE_WORKER = `
let clang = null;
self.onmessage = async (ev) => {
  const { id, source } = ev.data;
  let log = "";
  const dec = new TextDecoder();
  const sink = (b) => { if (b) log += dec.decode(b); };
  let last = -1;
  const report = ({ totalLength, doneLength }) => {
    const p = totalLength ? Math.min(doneLength / totalLength, 1) : 0;
    if (p - last >= 0.01 || (p === 1 && last < 1)) { last = p; self.postMessage({ id, progress: p }); }
  };
  try {
    if (!clang) {
      const mod = await import(${JSON.stringify(CLANG_URL)});
      // Prefetch with a progress callback: runClang's first internal step
      // ("-###") doesn't pass fetchProgress through.
      await mod.runClang(null, {}, { fetchProgress: report });
      clang = mod;
    }
    const files = await clang.runClang(
      ["clang++", "-std=c++17", "-O1", "-fno-exceptions", "-fno-color-diagnostics", "main.cpp", "-o", "main.wasm"],
      { "main.cpp": source },
      { stdout: sink, stderr: sink },
    );
    self.postMessage({ id, wasm: files["main.wasm"], log });
  } catch (e) {
    self.postMessage({ id, failed: true, log: log || String(e) });
  }
};
`;

const RUN_WORKER = `
self.onmessage = async (ev) => {
  const bytes = ev.data.wasm;
  const input = new TextEncoder().encode(ev.data.stdin || "");
  let inputAt = 0;
  let mem = null;
  const enc = new TextEncoder(), dec = new TextDecoder();
  const view = () => new DataView(mem.buffer);
  class Exit { constructor(code) { this.code = code; } }
  const wasi = {
    fd_write(fd, iovs, n, nwritten) {
      const v = view(); let total = 0, text = "";
      for (let i = 0; i < n; i++) {
        const p = v.getUint32(iovs + i * 8, true), l = v.getUint32(iovs + i * 8 + 4, true);
        text += dec.decode(new Uint8Array(mem.buffer, p, l)); total += l;
      }
      v.setUint32(nwritten, total, true);
      if (fd === 1 || fd === 2) self.postMessage({ chunk: text, fd });
      return 0;
    },
    proc_exit(code) { throw new Exit(code); },
    args_sizes_get(a, b) { view().setUint32(a, 0, true); view().setUint32(b, 0, true); return 0; },
    args_get() { return 0; },
    environ_sizes_get(a, b) { view().setUint32(a, 0, true); view().setUint32(b, 0, true); return 0; },
    environ_get() { return 0; },
    clock_time_get(id, prec, out) { view().setBigUint64(out, BigInt(Math.round(performance.now() * 1e6)), true); return 0; },
    random_get(p, l) { crypto.getRandomValues(new Uint8Array(mem.buffer, p, l)); return 0; },
    fd_fdstat_get(fd, out) { const v = view(); v.setUint8(out, 2); return 0; },
    fd_prestat_get() { return 8; },
    fd_read(fd, iovs, n, nread) {
      const v = view(); let total = 0;
      if (fd === 0) {
        for (let i = 0; i < n; i++) {
          const p = v.getUint32(iovs + i * 8, true), l = v.getUint32(iovs + i * 8 + 4, true);
          const take = Math.min(l, input.length - inputAt);
          new Uint8Array(mem.buffer, p, take).set(input.subarray(inputAt, inputAt + take));
          inputAt += take; total += take;
          if (take < l) break;
        }
      }
      v.setUint32(nread, total, true);
      return 0;
    },
    fd_close() { return 0; },
    fd_seek() { return 70; },
  };
  try {
    const mod = await WebAssembly.compile(bytes);
    const imports = { wasi_snapshot_preview1: {} };
    for (const imp of WebAssembly.Module.imports(mod)) {
      imports[imp.module] = imports[imp.module] || {};
      imports[imp.module][imp.name] = wasi[imp.name] || (() => 52);
    }
    const inst = await WebAssembly.instantiate(mod, imports);
    mem = inst.exports.memory;
    inst.exports._start();
    self.postMessage({ done: true, code: 0 });
  } catch (e) {
    if (e instanceof Exit) self.postMessage({ done: true, code: e.code });
    else self.postMessage({ done: true, crash: String(e && e.message || e) });
  }
};
`;

let compiler: Worker | null = null;
let seq = 0;
let loaded = false;

function compile(source: string, onStatus?: (s: string) => void): Promise<{ wasm?: Uint8Array; log: string }> {
  if (!compiler) compiler = makeWorker(COMPILE_WORKER, true);
  const w = compiler;
  const id = ++seq;
  onStatus?.(loaded ? "Compiling your C++…" : "Downloading the C++ compiler (about 23 MB, only the first time)…");
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      w.terminate();
      compiler = null;
      resolve({ log: "The compiler took too long. Check your connection and try again." });
    }, loaded ? 60_000 : 240_000);
    const onMsg = (ev: MessageEvent) => {
      const d = ev.data;
      if (d.id !== id) return;
      if (typeof d.progress === "number") {
        if (d.progress >= 1) {
          loaded = true;
          onStatus?.("Compiling your C++…");
        } else onStatus?.(`Downloading the C++ compiler… ${Math.round(d.progress * 100)}% (only the first time)`);
        return;
      }
      loaded = true;
      clearTimeout(timer);
      w.removeEventListener("message", onMsg);
      resolve(d.failed ? { log: d.log } : { wasm: d.wasm, log: d.log });
    };
    w.addEventListener("message", onMsg);
    w.postMessage({ id, source });
  });
}

export async function run(
  code: string,
  fn: string,
  sig: Signature,
  tests: TestInput[],
  timeoutMs: number,
  onStatus?: (s: string) => void,
): Promise<RunResult[]> {
  const { wasm, log } = await compile(cppProgram(code, fn, sig, tests), onStatus);
  if (!wasm) {
    const msg = cppCompileMessage(log);
    return tests.map(() => ({ output: null, error: `Your code didn't compile:\n${msg}`, stdout: "", ms: 0 }));
  }
  onStatus?.("Running tests…");
  const worker = makeWorker(RUN_WORKER);
  return new Promise<RunResult[]>((resolve) => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const t0 = performance.now();
    const finish = (extraError?: string) => {
      clearTimeout(timer);
      worker.terminate();
      const { results } = parseMarked(watch.text, tests.length);
      if (extraError && watch.current >= 0 && watch.current < tests.length) {
        results[watch.current] = { ...results[watch.current], output: null, error: extraError };
        for (let j = watch.current + 1; j < tests.length; j++) results[j] = { ...results[j], error: "Skipped because an earlier test stopped the program." };
      }
      const ms = (performance.now() - t0) / Math.max(1, tests.length);
      resolve(results.map((r) => ({ ...r, ms: r.ms || ms })));
    };
    const arm = () => {
      clearTimeout(timer);
      timer = setTimeout(() => finish(timeoutMessage(timeoutMs)), timeoutMs);
    };
    const watch = markerWatcher(arm);
    arm();
    worker.onmessage = (ev) => {
      const d = ev.data;
      if (typeof d.chunk === "string") watch.push(d.chunk);
      else if (d.done) {
        if (d.crash) finish(crashMessage(d.crash));
        else if (d.code) finish(`Your program stopped with exit code ${d.code}.`);
        else finish();
      }
    };
    worker.postMessage({ wasm });
  });
}

function crashMessage(crash: string): string {
  return /unreachable|out of bounds|memory access/i.test(crash)
    ? "Your program crashed, often from reading outside a vector or string, or dividing by zero."
    : `Your program crashed: ${crash}`;
}

/** "Run my code": compile the learner's program as it is and run its main(). */
export async function runProgram(code: string, stdin: string, timeoutMs: number, onStatus?: (s: string) => void): Promise<ProgramResult> {
  if (!hasCppMain(code)) {
    return programFailure(
      "missing",
      "There's no main() to start from. Add int main() { … } that calls your function, or use Run examples to test it.",
    );
  }
  const { wasm, log } = await compile(cppSource(code), onStatus);
  if (!wasm) return programFailure("compile", cppCompileMessage(log));
  onStatus?.("Running your code…");
  const worker = makeWorker(RUN_WORKER);
  const col = outputCollector();
  // Compiler warnings are worth seeing too.
  const warnings = cppCompileMessage(log);
  if (log.trim() && warnings !== "Your code didn't compile.") col.push("err", warnings + "\n");
  const t0 = performance.now();
  return new Promise<ProgramResult>((resolve) => {
    const done = (problem: ProgramResult["problem"], exitCode = 0) => {
      clearTimeout(timer);
      worker.terminate();
      resolve({ ...col.value, problem, exitCode, ms: performance.now() - t0 });
    };
    const timer = setTimeout(() => done({ kind: "timeout", message: programTimeoutMessage(timeoutMs) }), timeoutMs);
    worker.onmessage = (ev) => {
      const d = ev.data;
      if (typeof d.chunk === "string") col.push(d.fd === 2 ? "err" : "out", d.chunk);
      else if (d.done) {
        if (d.crash) done({ kind: "runtime", message: crashMessage(d.crash) });
        else done(null, d.code || 0);
      }
    };
    worker.postMessage({ wasm, stdin });
  });
}
