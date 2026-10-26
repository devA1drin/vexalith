/**
 * Java in the browser with CheerpJ (a JVM in WebAssembly by Leaning Technologies,
 * free under its Community License for FOSS projects) and OpenJDK 8's javac.
 * Everything runs in a hidden frame (public/runners/java.html); nothing is sent
 * to a server.
 *
 * CheerpJ runs on the page's thread, so a stuck loop can't simply be killed like a
 * worker. Instead every while/for condition in the learner's code gets a cheap
 * time check (see guardJavaLoops), which stops a test after its time limit.
 */
import { guardJavaLoops, javaCompileMessage, javaLayout, javaMain, javaProgram } from "./harness";
import { OUTPUT_LIMIT, programFailure, programTimeoutMessage, type ProblemKind, type ProgramResult, type RunResult, type Signature, type TestInput } from "./runner";

let frame: HTMLIFrameElement | null = null;
let frameReady: Promise<HTMLIFrameElement> | null = null;
let seq = 0;

function getFrame(): Promise<HTMLIFrameElement> {
  if (frame && frameReady) return frameReady;
  const f = document.createElement("iframe");
  f.src = "/runners/java.html";
  f.title = "Java runner";
  f.setAttribute("aria-hidden", "true");
  f.tabIndex = -1;
  f.style.cssText = "position:absolute;width:1px;height:1px;border:0;opacity:0;pointer-events:none;left:-9999px;top:0";
  frame = f;
  frameReady = new Promise((resolve) => {
    const onMsg = (ev: MessageEvent) => {
      if (ev.source === f.contentWindow && ev.data?.ready) {
        window.removeEventListener("message", onMsg);
        resolve(f);
      }
    };
    window.addEventListener("message", onMsg);
  });
  document.body.appendChild(f);
  return frameReady;
}

function resetFrame() {
  frame?.remove();
  frame = null;
  frameReady = null;
}

type FrameReply = { failed?: string; compileError?: string; results?: string };
type JavaFile = { name: string; text: string };

/** Compile the files and run `run` in the Java frame; resolves with the frame's reply. */
async function inFrame(
  files: (outFile: string) => JavaFile[],
  run: string,
  budgetMs: number,
  onStatus?: (s: string) => void,
): Promise<FrameReply & { stuck?: boolean; ranMs?: number }> {
  onStatus?.("Starting Java (the first time takes a little while)…");
  const f = await getFrame();
  const id = ++seq;
  const outFile = `/files/vx-out-${id}.txt`;
  let started = 0;
  return new Promise((resolve) => {
    // Backstop in case the runner itself gets stuck: generous, because the first run downloads Java.
    const timer = setTimeout(() => {
      done();
      resetFrame();
      resolve({ stuck: true });
    }, 180_000 + budgetMs);
    const done = () => {
      clearTimeout(timer);
      window.removeEventListener("message", onMsg);
    };
    const onMsg = (ev: MessageEvent) => {
      if (ev.source !== f.contentWindow || ev.origin !== window.location.origin || ev.data?.id !== id) return;
      const d = ev.data;
      if (d.status) {
        if (d.status === "Running…") started = performance.now();
        return onStatus?.(d.status === "Running…" ? (run === "VxMain" ? "Running tests…" : "Running your code…") : d.status);
      }
      done();
      resolve({ ...d, ranMs: started ? performance.now() - started : 0 });
    };
    window.addEventListener("message", onMsg);
    f.contentWindow?.postMessage({ id, files: files(outFile), run, outFile, msgFile: `/files/vx-javac-${id}.txt` }, window.location.origin);
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
  const fail = (error: string) => tests.map(() => ({ output: null, error, stdout: "", ms: 0 }));
  const layout = javaLayout(code, fn);
  const target = layout.target;
  if (!target) {
    return fail(`I couldn't find a method called ${fn}. Keep it inside class Solution, with the same name as in the starter code.`);
  }
  const d = await inFrame(
    (outFile) => [
      { name: layout.file, text: guardJavaLoops(code) },
      { name: "VxMain.java", text: javaMain(fn, sig, tests, timeoutMs, outFile, target, layout.file) },
    ],
    "VxMain",
    timeoutMs * tests.length,
    onStatus,
  );
  if (d.stuck) return fail("Java took too long to respond, so I restarted it. Check your connection, then try again.");
  if (d.failed) return fail(`Java couldn't run: ${d.failed}`);
  if (typeof d.compileError === "string") return fail(`Your code didn't compile:\n${javaCompileMessage(d.compileError, layout.file)}`);
  const results: RunResult[] = fail("Your code stopped before it returned an answer.");
  for (const line of String(d.results || "").split("\n")) {
    if (!line.trim()) continue;
    try {
      const r = JSON.parse(line);
      if (r.i >= 0 && r.i < tests.length) results[r.i] = { output: r.output, error: r.error, stdout: r.stdout || "", ms: r.ms || 0 };
    } catch {
      /* ignore a broken line */
    }
  }
  return results;
}

/** "Run my code": compile the learner's classes and run their main(). */
export async function runProgram(code: string, stdin: string, timeoutMs: number, onStatus?: (s: string) => void): Promise<ProgramResult> {
  const layout = javaLayout(code);
  const mainClass = layout.mainClass;
  if (!mainClass) {
    return programFailure(
      "missing",
      "There's no main method to start from. Add public static void main(String[] args) { … } that calls your method, or use Run examples to test it.",
    );
  }
  const d = await inFrame(
    (outFile) => [
      { name: layout.file, text: guardJavaLoops(code) },
      { name: "VxProgram.java", text: javaProgram(mainClass, stdin, timeoutMs, outFile, layout.file) },
    ],
    "VxProgram",
    timeoutMs,
    onStatus,
  );
  if (d.stuck) return programFailure("load", "Java took too long to respond, so I restarted it. Check your connection, then try again.");
  if (d.failed) return programFailure("runtime", `Java couldn't run: ${d.failed}`);
  if (typeof d.compileError === "string") return programFailure("compile", javaCompileMessage(d.compileError, layout.file));
  try {
    const r = JSON.parse(String(d.results || ""));
    const kind = (r.kind ?? null) as ProblemKind | null;
    const problem =
      kind === "timeout"
        ? { kind, message: programTimeoutMessage(timeoutMs) }
        : kind
          ? { kind, message: kind === "input" ? `${r.error}: your program asked for more input than the Input box has.` : String(r.error) }
          : null;
    return {
      stdout: r.stdout || "",
      stderr: r.stderr || "",
      problem,
      exitCode: r.exit || 0,
      ms: d.ranMs ?? 0,
      truncated: (r.stdout || "").length >= OUTPUT_LIMIT || (r.stderr || "").length >= OUTPUT_LIMIT,
    };
  } catch {
    return programFailure("runtime", "Your program stopped before it finished, so its output was lost.");
  }
}
