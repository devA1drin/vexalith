"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type ExerciseDetail, type SubmitOut } from "@/lib/api";
import { CodeEditor } from "@/components/CodeEditor";
import { SolvePanel } from "@/components/SolvePanel";
import { CODE_LANGUAGES } from "@/lib/codeLanguages";
import { errorTip, wrongTip } from "@/lib/codeHelp";
import { runTests, sameValue, show, showOutput, type RunResult } from "@/lib/runner";

const HOW_KEY = "vexalith_how_to_code_open";

type Row = {
  index: number;
  visible: boolean;
  args: unknown[];
  expected?: unknown;
  result: RunResult;
  passed: boolean;
};

/** Render `backtick` spans in a task description as inline code. */
function TaskText({ text }: { text: string }) {
  return (
    <>
      {text.split(/(`[^`]+`)/g).map((part, i) =>
        part.startsWith("`") && part.endsWith("`") ? (
          <code key={i} className="break-words bg-ink-800 px-1 py-0.5 font-mono text-[0.9em] text-ink-50">
            {part.slice(1, -1)}
          </code>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  );
}

function HowToRun({ language }: { language: string }) {
  const [open, setOpen] = useState(true);
  useEffect(() => setOpen(localStorage.getItem(HOW_KEY) !== "0"), []);
  return (
    <details
      className="border border-ink-700 bg-ink-900/60 px-4 py-3"
      open={open}
      onToggle={(e) => {
        const o = (e.currentTarget as HTMLDetailsElement).open;
        setOpen(o);
        localStorage.setItem(HOW_KEY, o ? "1" : "0");
      }}
      data-testid="how-to-answer"
      data-kind="code"
    >
      <summary className="cursor-pointer font-mono text-[12px] uppercase tracking-wider text-ink-200">
        How to answer · <span className="text-accent">write and test a function</span>
      </summary>
      <ol className="mt-3 space-y-1.5 text-sm text-ink-200">
        <li className="flex gap-2.5"><span className="font-mono text-[12px] text-accent">1.</span><span>Finish the function in the editor. Keep its name, and return the answer (don&apos;t just print it).</span></li>
        <li className="flex gap-2.5"><span className="font-mono text-[12px] text-accent">2.</span><span><b className="text-ink-50">Run</b> tries the example tests. Anything you print shows up under each test{language === "java" ? " (System.out works)" : ""}.</span></li>
        <li className="flex gap-2.5"><span className="font-mono text-[12px] text-accent">3.</span><span><b className="text-ink-50">Submit</b> also runs the hidden tests and saves your result. Try edge cases like an empty input.</span></li>
      </ol>
    </details>
  );
}

export default function ExercisePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const [ex, setEx] = useState<ExerciseDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState<null | "run" | "submit">(null);
  const [rows, setRows] = useState<Row[] | null>(null);
  const [verdict, setVerdict] = useState<SubmitOut | null>(null);
  const [tried, setTried] = useState(false);
  const draftKey = `vexalith_code_${slug}`;

  useEffect(() => {
    api.exercise(slug).then((d) => {
      setEx(d);
      setCode(localStorage.getItem(draftKey) ?? d.starter);
    }).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = `/login?callbackUrl=/code/${slug}`;
      else setError(e instanceof ApiError && e.status === 404 ? "That exercise doesn't exist." : e instanceof Error ? e.message : "Failed to load");
    });
  }, [slug, draftKey]);

  const update = (v: string) => {
    setCode(v);
    localStorage.setItem(draftKey, v);
  };

  const execute = useCallback(
    async (mode: "run" | "submit") => {
      if (!ex || busy) return;
      setBusy(mode);
      setVerdict(null);
      setError(null);
      const tests = mode === "run" ? ex.visible_tests : [...ex.visible_tests, ...ex.hidden_tests];
      try {
        const results = await runTests({
          language: ex.language,
          code,
          fn: ex.function,
          tests: tests.map((t) => ({ args: t.args })),
          timeoutMs: ex.timeout_ms,
          signature: ex.signature,
          onStatus: setStatus,
        });
        let next: Row[] = results.map((r, i) => {
          const visible = i < ex.visible_tests.length;
          const expected = visible ? ex.visible_tests[i].expected : undefined;
          return { index: i, visible, args: tests[i].args, expected, result: r, passed: visible && r.error === null && sameValue(r.output, expected) };
        });
        if (mode === "submit") {
          setStatus("Checking the hidden tests…");
          const out = await api.submitExercise(
            ex.slug,
            code,
            results.map((r) => ({ output: r.output === null ? null : r.output.slice(0, 4000), error: r.error === null ? null : r.error.slice(0, 900) })),
          );
          next = next.map((row) => ({ ...row, passed: out.checks[row.index]?.passed ?? false }));
          setVerdict(out);
          setEx({ ...ex, help: out.help, attempted: true, ...(out.solved ? { solved: true, best_passed: out.total } : {}) });
        }
        setRows(next);
        setTried(true);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong while running your code.");
      } finally {
        setStatus(null);
        setBusy(null);
      }
    },
    [ex, busy, code],
  );

  if (error && !ex) {
    return (
      <div className="space-y-4">
        <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>
        <Link href="/code" className="btn-ghost">← All exercises</Link>
      </div>
    );
  }
  if (!ex) return <div className="card h-96 animate-pulse" />;

  const info = CODE_LANGUAGES[ex.language];
  const visibleRows = rows?.filter((r) => r.visible) ?? [];
  const hiddenRows = rows?.filter((r) => !r.visible) ?? [];
  const passedCount = rows?.filter((r) => r.passed).length ?? 0;
  // A compile error (or anything else that stops every test the same way) is shown once, not per test.
  const firstError = rows?.[0]?.result.error ?? null;
  const sharedError = rows && rows.length > 1 && firstError && rows.every((r) => r.result.error === firstError) ? firstError : null;

  return (
    <div className="space-y-6">
      <div className="border-b border-ink-700 pb-5">
        <Link href="/code" className="label mb-3 inline-block hover:text-ink-50">← 02 · Code</Link>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h1 className="font-display text-3xl font-bold tracking-tight text-ink-50 sm:text-4xl">{ex.title}</h1>
          {ex.solved && (
            <span className="chip border-accent text-accent" data-testid="solved-chip">
              {ex.help.solved_with_help ? "✓ Solved with help" : "✓ Solved"}
            </span>
          )}
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="chip text-ink-100">{info.name}</span>
          <span className="chip">{ex.difficulty}</span>
          <span className="chip">{ex.topic}</span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0 space-y-4">
          <div className="card p-4" data-testid="task">
            <p className="label mb-2">Your task</p>
            <p className="text-[15px] leading-relaxed text-ink-100"><TaskText text={ex.description} /></p>
          </div>
          <HowToRun language={ex.language} />
          <div className="card p-4">
            <p className="label mb-3">Example tests</p>
            <ul className="space-y-2 font-mono text-[13px]">
              {ex.visible_tests.map((t, i) => (
                <li key={i} className="break-words text-ink-200">
                  <span className="text-ink-50">{ex.function}({t.args.map((a) => show(a, ex.language)).join(", ")})</span>
                  <span className="text-ink-500"> → </span>
                  <span className="text-accent">{show(t.expected, ex.language)}</span>
                </li>
              ))}
            </ul>
            <p className="mt-3 text-[13px] text-ink-400">+ {ex.hidden_tests.length} hidden test{ex.hidden_tests.length === 1 ? "" : "s"} when you submit.</p>
          </div>
          <SolvePanel
            slug={ex.slug}
            language={ex.language}
            help={ex.help}
            tried={tried || ex.attempted}
            solved={ex.solved}
            onChange={(help) => setEx((cur) => (cur ? { ...cur, help } : cur))}
          />
        </div>

        <div className="min-w-0 space-y-3">
          <div className="flex items-center justify-between gap-2">
            <span className="label">Your code · {info.name}</span>
            <button className="font-mono text-[11px] uppercase tracking-wider text-ink-400 hover:text-ink-50" onClick={() => update(ex.starter)} disabled={!!busy}>
              Reset
            </button>
          </div>
          <CodeEditor value={code} onChange={update} onRun={() => execute("run")} indent={ex.language === "javascript" ? "  " : "    "} label={`${info.name} code editor`} />
          <div className="flex flex-wrap items-center gap-3">
            <button className="btn-ghost" onClick={() => execute("run")} disabled={!!busy} data-testid="run">
              {busy === "run" ? "Running…" : "Run examples"}
            </button>
            <button className="btn-primary" onClick={() => execute("submit")} disabled={!!busy} data-testid="submit">
              {busy === "submit" ? "Checking…" : <>Submit <span className="btn-arrow">→</span></>}
            </button>
            <span className="font-mono text-[11px] text-ink-500 max-sm:hidden">Ctrl + Enter runs</span>
          </div>
          {status && (
            <p className="flex items-center gap-2 font-mono text-[12px] text-ink-300" role="status" data-testid="run-status">
              <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-ink-600 border-t-accent" />
              {status}
            </p>
          )}
          {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
          <p className="text-[12px] leading-relaxed text-ink-500">
            Runs in your browser on {info.engine}, {info.firstLoad}. Each test stops after {Math.round(ex.timeout_ms / 1000)} s.
            {info.credit && <> {info.credit}</>}
          </p>
        </div>
      </div>

      {rows && (
        <section className="space-y-3" data-testid="results" aria-live="polite">
          {verdict ? (
            <div className={`border-l-2 pl-4 ${verdict.solved ? "border-accent" : "border-signal"}`} data-testid="verdict">
              <p className="font-display text-xl font-semibold text-ink-50">{verdict.passed} of {verdict.total} tests passed</p>
              <p className="text-sm text-ink-300">{verdict.first_solve
                  ? verdict.help.solved_with_help
                    ? "Solved with help. It's saved to your progress; try the next one with hints first."
                    : "First solve! It's saved to your progress."
                  : verdict.message}</p>
            </div>
          ) : (
            <p className="label">{passedCount} of {rows.length} example tests passed</p>
          )}
          {sharedError ? (
            <div className="card border-l-2 border-l-signal p-3" data-testid="shared-error">
              <p className="label">None of the {rows.length} tests could run</p>
              <pre className="mt-2 whitespace-pre-wrap break-words font-mono text-[12px] text-signal-soft">{sharedError}</pre>
              {errorTip(sharedError, ex.language) && <p className="mt-1.5 text-sm text-ink-300">Tip: {errorTip(sharedError, ex.language)}</p>}
            </div>
          ) : (
          <>
          <ul className="space-y-2">
            {visibleRows.map((r) => (
              <TestRow key={r.index} row={r} ex={ex} />
            ))}
          </ul>
          {hiddenRows.length > 0 && (
            <ul className="space-y-2" data-testid="hidden-results">
              {hiddenRows.map((r) => (
                <TestRow key={r.index} row={r} ex={ex} />
              ))}
            </ul>
          )}
          </>
          )}
        </section>
      )}
    </div>
  );
}

/** Long inputs (e.g. a 500-item list) are cut so a test row stays readable. */
function shorten(text: string, max = 160): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function TestRow({ row, ex }: { row: Row; ex: ExerciseDetail }) {
  const { result: r, passed } = row;
  const call = shorten(`${ex.function}(${row.args.map((a) => show(a, ex.language)).join(", ")})`);
  let got: unknown;
  try {
    got = r.output === null ? null : JSON.parse(r.output);
  } catch {
    got = undefined;
  }
  const tip = r.error ? errorTip(r.error, ex.language) : !passed && row.visible ? wrongTip(got, row.expected, ex.language) : null;
  return (
    <li className={`card border-l-2 p-3 ${passed ? "border-l-accent" : "border-l-signal"}`} data-testid={passed ? "test-pass" : "test-fail"}>
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className={`font-mono text-[12px] uppercase tracking-wider ${passed ? "text-accent" : "text-signal-soft"}`}>
          {passed ? "✓ Pass" : "✗ Fail"}
        </span>
        <span className="label">{row.visible ? `Example ${row.index + 1}` : `Hidden test ${row.index + 1}`}</span>
        <code className="min-w-0 break-all font-mono text-[13px] text-ink-100">{call}</code>
      </div>
      {!passed && (
        <div className="mt-2 space-y-1.5 text-sm">
          {r.error ? (
            <pre className="whitespace-pre-wrap break-words font-mono text-[12px] text-signal-soft">{r.error}</pre>
          ) : row.visible ? (
            <p className="font-mono text-[13px] text-ink-200">
              Expected <span className="text-accent">{show(row.expected, ex.language)}</span>, but your function returned{" "}
              <span className="text-signal-soft">{r.output === null ? "nothing" : showOutput(r.output, ex.language)}</span>.
            </p>
          ) : (
            <p className="text-ink-300">
              Your function returned <span className="font-mono text-signal-soft">{r.output === null ? "nothing" : showOutput(r.output, ex.language)}</span>,
              which isn&apos;t right for this input. Try it by hand, or add it as a print to check.
            </p>
          )}
          {tip && <p className="text-ink-300">Tip: {tip}</p>}
        </div>
      )}
      {r.stdout.trim() && (
        <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap break-words border-t border-ink-800 pt-2 font-mono text-[12px] text-ink-400">
          <span className="label">Printed · </span>
          {r.stdout.trimEnd()}
        </pre>
      )}
    </li>
  );
}
