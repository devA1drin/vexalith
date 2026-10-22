"use client";

import { useEffect, useState } from "react";
import { api, type HintsOut } from "@/lib/api";

/**
 * Progressive hints for the current question: revealed one level at a time.
 * Each hint takes 10% off this answer's score (max 30%), so the cost is shown
 * on the button before you click.
 */
export function HintPanel({ questionId, hintCount, locked }: { questionId: number; hintCount: number; locked: boolean }) {
  const [data, setData] = useState<HintsOut | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    setData(null);
    setError(null);
    if (hintCount > 0) api.hints(questionId).then((d) => alive && setData(d)).catch(() => {});
    return () => {
      alive = false;
    };
  }, [questionId, hintCount]);

  if (hintCount === 0) return null;
  const revealed = data?.revealed ?? [];
  const per = Math.round((data?.penalty_per_hint ?? 0.1) * 100);
  const done = revealed.length >= hintCount;

  async function reveal() {
    setBusy(true);
    setError(null);
    try {
      setData(await api.revealHint(questionId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load the hint");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="border border-ink-700" data-testid="hint-panel">
      <div className="flex items-center justify-between gap-3 border-b border-ink-700 px-4 py-2">
        <span className="label">Hints · {revealed.length}/{hintCount}</span>
        {revealed.length > 0 && (
          <span className="font-mono text-[11px] text-ink-500">−{Math.round((data?.penalty ?? 0) * 100)}% on this answer</span>
        )}
      </div>
      {revealed.length > 0 && (
        <ol className="divide-y divide-ink-800">
          {revealed.map((h, i) => (
            <li key={i} className="q-enter grid grid-cols-[2rem_1fr] gap-2 px-4 py-3 text-sm leading-relaxed text-ink-100" data-testid="hint">
              <span className="font-mono text-[12px] text-accent">{String(i + 1).padStart(2, "0")}</span>
              <span>{h}</span>
            </li>
          ))}
        </ol>
      )}
      {!locked && !done && (
        <button
          type="button"
          onClick={reveal}
          disabled={busy}
          data-testid="reveal-hint"
          className="flex w-full items-center justify-between border-t border-ink-800 px-4 py-2.5 text-left font-mono text-[12px] uppercase tracking-wider text-ink-300 transition-colors first:border-t-0 hover:bg-ink-900 hover:text-accent disabled:opacity-60"
        >
          <span>{busy ? "Thinking…" : revealed.length === 0 ? "Need a nudge? Show hint 1" : `Show hint ${revealed.length + 1}`}</span>
          <span className="text-ink-500">−{per}%</span>
        </button>
      )}
      {error && <p role="alert" className="px-4 py-2 text-sm text-signal-soft">{error}</p>}
    </div>
  );
}
