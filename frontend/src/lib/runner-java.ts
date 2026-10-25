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
import { guardJavaLoops, javaCompileMessage, javaMain } from "./harness";
import type { RunResult, Signature, TestInput } from "./runner";

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

export async function run(
  code: string,
  fn: string,
  sig: Signature,
  tests: TestInput[],
  timeoutMs: number,
  onStatus?: (s: string) => void,
): Promise<RunResult[]> {
  const fail = (error: string) => tests.map(() => ({ output: null, error, stdout: "", ms: 0 }));
  if (!/\bclass\s+Solution\b/.test(code)) return fail("Keep your code inside class Solution, like in the starter code.");
  onStatus?.("Starting Java (the first time takes a little while)…");
  const f = await getFrame();
  const id = ++seq;
  const outFile = `/files/vx-out-${id}.txt`;
  const msgFile = `/files/vx-javac-${id}.txt`;
  return new Promise<RunResult[]>((resolve) => {
    // Backstop in case the runner itself gets stuck: generous, because the first run downloads Java.
    const limit = 180_000 + timeoutMs * tests.length;
    const timer = setTimeout(() => {
      done();
      resetFrame();
      resolve(fail("Java took too long to respond, so I restarted it. Check your connection, then try again."));
    }, limit);
    const done = () => {
      clearTimeout(timer);
      window.removeEventListener("message", onMsg);
    };
    const onMsg = (ev: MessageEvent) => {
      if (ev.source !== f.contentWindow || ev.origin !== window.location.origin || ev.data?.id !== id) return;
      const d = ev.data;
      if (d.status) return onStatus?.(d.status);
      done();
      if (d.failed) return resolve(fail(`Java couldn't run: ${d.failed}`));
      if (typeof d.compileError === "string") return resolve(fail(`Your code didn't compile:\n${javaCompileMessage(d.compileError)}`));
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
      resolve(results);
    };
    window.addEventListener("message", onMsg);
    f.contentWindow?.postMessage(
      { id, solution: guardJavaLoops(code), main: javaMain(fn, sig, tests, timeoutMs, outFile), outFile, msgFile },
      window.location.origin,
    );
  });
}
