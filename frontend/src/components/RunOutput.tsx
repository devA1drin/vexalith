"use client";

import type { ReactNode } from "react";
import type { CodeLanguage } from "@/lib/api";
import { errorTip } from "@/lib/codeHelp";
import { OUTPUT_LIMIT, type ProblemKind, type ProgramResult } from "@/lib/runner";

/** The Output panel's frame: a title bar with a short summary, then the body. */
export function OutputFrame({ meta, children }: { meta?: ReactNode; children: ReactNode }) {
  return (
    <section className="card min-w-0" data-testid="output" aria-live="polite">
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-ink-700 px-4 py-2.5">
        <span className="label text-ink-200">Output</span>
        {meta && <span className="font-mono text-[11px] text-ink-400" data-testid="output-meta">{meta}</span>}
      </div>
      <div className="space-y-3 p-4">{children}</div>
    </section>
  );
}

/** Shown while a runtime downloads, compiles or runs. A percent in the status fills the bar. */
export function RunLoading({ status }: { status: string }) {
  const pct = /(\d{1,3})%/.exec(status);
  const value = pct ? Math.min(100, Number(pct[1])) : null;
  return (
    <div className="space-y-2.5" data-testid="run-loading">
      <p className="flex items-start gap-2.5 font-mono text-[12px] text-ink-200" role="status" data-testid="run-status">
        <span className="mt-0.5 inline-block h-3 w-3 shrink-0 animate-spin rounded-full border-2 border-ink-600 border-t-accent" />
        <span className="min-w-0">{status}</span>
      </p>
      <div className="h-1 overflow-hidden bg-ink-800" aria-hidden="true">
        {value === null ? (
          <div className="h-full w-1/3 animate-[vx-indeterminate_1.2s_ease-in-out_infinite] bg-accent/70" />
        ) : (
          <div className="h-full bg-accent transition-[width] duration-300" style={{ width: `${value}%` }} />
        )}
      </div>
    </div>
  );
}

const TITLES: Record<ProblemKind, string> = {
  compile: "Your code didn't compile",
  runtime: "Your program stopped with an error",
  timeout: "Your program took too long",
  input: "Your program wanted more input",
  missing: "Nothing to start from yet",
  load: "The runtime couldn't start",
};

function Block({ label, tone, children, testid }: { label: string; tone: "out" | "err"; children: ReactNode; testid: string }) {
  return (
    <div className="min-w-0">
      <p className={`label mb-1.5 ${tone === "err" ? "text-signal-soft" : ""}`}>{label}</p>
      <pre
        className={`max-h-80 overflow-auto whitespace-pre-wrap break-words border bg-ink-950 px-3 py-2.5 font-mono text-[13px] leading-relaxed ${
          tone === "err" ? "border-signal/40 text-signal-soft" : "border-ink-700 text-ink-50"
        }`}
        style={{ fontVariantLigatures: "none" }}
        data-testid={testid}
      >
        {children}
      </pre>
    </div>
  );
}

/**
 * What "Run my code" produced: the program's printed output, anything written to
 * the error stream, and, when it stopped early, what went wrong in plain words.
 */
export function ProgramOutput({
  result,
  language,
  callHint,
  onShowInput,
}: {
  result: ProgramResult;
  language: CodeLanguage;
  /** A line that would call the exercise function, for programs that print nothing. */
  callHint: string;
  onShowInput: () => void;
}) {
  const { stdout, stderr, problem, exitCode, truncated } = result;
  const tip = problem && (problem.kind === "compile" || problem.kind === "runtime") ? errorTip(problem.message, language) : null;
  const printedNothing = !stdout.trim() && !stderr.trim();
  return (
    <>
      {problem && (
        <div className="border-l-2 border-signal pl-3" data-testid="program-problem" data-kind={problem.kind}>
          <p className="font-display text-[15px] font-semibold text-ink-50">{TITLES[problem.kind]}</p>
          <pre className="mt-1.5 whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-signal-soft" style={{ fontVariantLigatures: "none" }}>
            {problem.message}
          </pre>
          {tip && <p className="mt-1.5 text-sm text-ink-300">Tip: {tip}</p>}
          {problem.kind === "input" && (
            <p className="mt-1.5 text-sm text-ink-300">
              Put each value on its own line in the{" "}
              <button type="button" className="text-accent underline-offset-2 hover:underline" onClick={onShowInput}>
                Input box
              </button>
              , then run it again.
            </p>
          )}
          {problem.kind === "missing" && callHint && (
            <pre className="mt-2 overflow-x-auto border border-ink-700 bg-ink-950 px-3 py-2 font-mono text-[12px] text-ink-100">{callHint}</pre>
          )}
        </div>
      )}
      {stdout && <Block label="Printed" tone="out" testid="stdout">{stdout.replace(/\n$/, "")}</Block>}
      {stderr.trim() && <Block label="Errors and warnings" tone="err" testid="stderr">{stderr.replace(/\n$/, "")}</Block>}
      {printedNothing && !problem && (
        <div className="text-sm text-ink-300" data-testid="printed-nothing">
          <p>Your program ran without printing anything.</p>
          {callHint && (
            <>
              <p className="mt-1.5">Nothing calls your function yet. To see its answer, add:</p>
              <pre className="mt-1.5 overflow-x-auto border border-ink-700 bg-ink-950 px-3 py-2 font-mono text-[12px] text-ink-100">{callHint}</pre>
            </>
          )}
        </div>
      )}
      {(exitCode !== 0 || truncated) && (
        <p className="font-mono text-[11px] text-ink-400">
          {exitCode !== 0 && <>Ended with exit code {exitCode}. </>}
          {truncated && <>Output was cut off after {OUTPUT_LIMIT.toLocaleString("en-US")} characters.</>}
        </p>
      )}
    </>
  );
}
