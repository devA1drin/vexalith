"use client";

import { useEffect, useState } from "react";
import { api, type ExerciseHelp } from "@/lib/api";
import { CodeBlock } from "@/components/CodeBlock";

type Tab = "hints" | "explanation";

/**
 * "How to solve it" for a coding exercise.
 *
 * - Hints: up to 3, revealed one at a time.
 * - Explanation: the general idea, approach, pitfalls and reusable pattern, plus the
 *   reference solution. It unlocks when you pass every test, or when you choose to reveal
 *   it (straight away after a run, or after an "Are you sure?" before your first try).
 */
export function SolvePanel({
  slug,
  language,
  help,
  tried,
  solved,
  onChange,
}: {
  slug: string;
  language: string;
  help: ExerciseHelp;
  tried: boolean;
  solved: boolean;
  onChange: (h: ExerciseHelp) => void;
}) {
  const unlocked = !!help.explanation;
  const [tab, setTab] = useState<Tab>(unlocked ? "explanation" : "hints");
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Passing (or revealing) opens the explanation automatically.
  useEffect(() => {
    if (unlocked) setTab("explanation");
  }, [unlocked]);

  async function call(fn: () => Promise<ExerciseHelp>) {
    setBusy(true);
    setError(null);
    try {
      onChange(await fn());
      setConfirming(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  const reveal = () => (tried ? call(() => api.revealSolution(slug, true)) : setConfirming(true));
  const hintsLeft = help.hints.length < help.hint_count;

  return (
    <section className="card" aria-labelledby="solve-h" data-testid="solve-panel">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-ink-700 px-4 py-2.5">
        <h2 id="solve-h" className="label text-ink-100">How to solve it</h2>
        <div role="tablist" aria-label="How to solve it" className="flex border border-ink-700">
          {(["hints", "explanation"] as const).map((t) => (
            <button
              key={t}
              role="tab"
              type="button"
              aria-selected={tab === t}
              onClick={() => setTab(t)}
              data-testid={`solve-tab-${t}`}
              className={`px-3 py-1 font-mono text-[11px] uppercase tracking-wider transition-colors ${
                tab === t ? "bg-ink-50 text-ink-950" : "text-ink-300 hover:text-ink-50"
              }`}
            >
              {t === "hints" ? `Hints ${help.hints.length}/${help.hint_count}` : unlocked ? "Explanation" : "Explanation · locked"}
            </button>
          ))}
        </div>
      </div>

      {tab === "hints" ? (
        <div role="tabpanel" data-testid="solve-hints">
          {help.hints.length === 0 ? (
            <p className="px-4 py-3 text-sm text-ink-400">Stuck? Open a hint. Each one gives a little more away, from a nudge to the key technique.</p>
          ) : (
            <ol className="divide-y divide-ink-800">
              {help.hints.map((h, i) => (
                <li key={i} className="q-enter grid grid-cols-[2rem_1fr] gap-2 px-4 py-3 text-sm leading-relaxed text-ink-100" data-testid="exercise-hint">
                  <span className="font-mono text-[12px] text-accent">{String(i + 1).padStart(2, "0")}</span>
                  <span>{h}</span>
                </li>
              ))}
            </ol>
          )}
          {hintsLeft && (
            <button
              type="button"
              onClick={() => call(() => api.exerciseHint(slug))}
              disabled={busy}
              data-testid="exercise-reveal-hint"
              className="flex w-full items-center justify-between border-t border-ink-800 px-4 py-2.5 text-left font-mono text-[12px] uppercase tracking-wider text-ink-300 transition-colors hover:bg-ink-900 hover:text-accent disabled:opacity-60"
            >
              <span>{busy ? "Thinking…" : `Show hint ${help.hints.length + 1}`}</span>
              <span className="text-ink-500">{help.hint_count - help.hints.length} left</span>
            </button>
          )}
          <p className="border-t border-ink-800 px-4 py-2 text-[12px] text-ink-500">
            Exercises aren&apos;t scored, so hints are free. Revealing the solution before you pass marks the exercise &quot;solved with help&quot;.
          </p>
        </div>
      ) : (
        <div role="tabpanel" data-testid="solve-explanation">
          {help.explanation ? (
            <Explanation help={help} language={language} solved={solved} />
          ) : (
            <div className="space-y-3 px-4 py-4 text-sm">
              <p className="text-ink-300">
                The explanation and a reference solution open when you pass every test. Want them now? You can reveal them
                {tried ? "." : " after your first run, or right away if you're sure."}
              </p>
              {confirming ? (
                <div className="border border-signal/60 p-3" data-testid="reveal-confirm">
                  <p className="text-ink-100">Are you sure? You haven&apos;t run your code yet. Showing the solution marks this exercise &quot;solved with help&quot;.</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button type="button" className="btn-ghost" onClick={() => call(() => api.revealSolution(slug, true))} disabled={busy} data-testid="reveal-yes">
                      Yes, show it
                    </button>
                    <button type="button" className="btn-ghost" onClick={() => setConfirming(false)} disabled={busy}>
                      Keep trying
                    </button>
                  </div>
                </div>
              ) : (
                <button type="button" className="btn-ghost" onClick={reveal} disabled={busy} data-testid="reveal-solution">
                  {busy ? "Opening…" : "Show solution"}
                </button>
              )}
            </div>
          )}
        </div>
      )}
      {error && <p role="alert" className="px-4 pb-3 text-sm text-signal-soft">{error}</p>}
    </section>
  );
}

function Explanation({ help, language, solved }: { help: ExerciseHelp; language: string; solved: boolean }) {
  const x = help.explanation!;
  return (
    <div className="space-y-5 px-4 py-4">
      {help.solved_with_help && (
        <p className="chip border-ink-500 text-ink-200" data-testid="with-help-chip">Solved with help</p>
      )}
      <div>
        <p className="label mb-1.5">The idea</p>
        <p className="text-[15px] leading-relaxed text-ink-50">{x.idea}</p>
      </div>
      <div>
        <p className="label mb-1.5">Approach</p>
        <ol className="space-y-1.5 text-sm text-ink-200">
          {x.approach.map((s, i) => (
            <li key={i} className="flex gap-2.5">
              <span className="font-mono text-[12px] text-accent">{i + 1}.</span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      </div>
      <div>
        <p className="label mb-1.5">Watch out for</p>
        <ul className="space-y-1.5 text-sm text-ink-200">
          {x.pitfalls.map((s, i) => (
            <li key={i} className="flex gap-2.5">
              <span className="text-signal-soft" aria-hidden>!</span>
              <span>{s}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="border-l-2 border-accent pl-3">
        <p className="label mb-1 text-accent">Reuse this pattern</p>
        <p className="text-sm text-ink-100">{x.pattern}</p>
      </div>
      {help.solution && (
        <div data-testid="reference-solution">
          <p className="label mb-1.5">{solved ? "Compare with a reference solution" : "Reference solution"}</p>
          <CodeBlock code={help.solution} language={language} filename="solution" />
        </div>
      )}
    </div>
  );
}
