"use client";

import { useEffect, useRef, useState } from "react";
import { confirmMatches } from "@/lib/adminFormat";

/** A typed confirmation for destructive admin actions. */
export function ConfirmDialog({
  title, word, action, busy, error, onConfirm, onClose, children,
}: {
  title: string;
  word: string;
  action: string;
  busy?: boolean;
  error?: string | null;
  onConfirm: (typed: string) => void;
  onClose: () => void;
  children: React.ReactNode;
}) {
  const [typed, setTyped] = useState("");
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    input.current?.focus();
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", esc);
    return () => document.removeEventListener("keydown", esc);
  }, [onClose]);
  const ok = confirmMatches(word, typed);
  return (
    <div className="fixed inset-0 z-[60] flex items-end justify-center bg-ink-950/80 p-3 sm:items-center" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" className="w-full max-w-md border border-signal bg-ink-950 shadow-[8px_8px_0_0_rgba(255,91,46,0.25)]" data-testid="confirm-dialog">
        <div className="flex items-center gap-2 border-b border-ink-700 bg-signal/10 px-4 py-2.5">
          <span className="h-2 w-2 bg-signal" aria-hidden="true" />
          <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-signal">Can&apos;t be undone</span>
        </div>
        <form className="space-y-4 p-4 sm:p-5" onSubmit={(e) => { e.preventDefault(); if (ok && !busy) onConfirm(typed); }}>
          <h2 id="confirm-title" className="font-display text-2xl leading-tight text-ink-50">{title}</h2>
          <div className="space-y-2 text-[14px] leading-relaxed text-ink-300">{children}</div>
          <label className="block space-y-1.5">
            <span className="text-[13px] text-ink-300">Type <span className="font-mono text-ink-50">{word}</span> to confirm</span>
            <input ref={input} className="input font-mono" value={typed} onChange={(e) => setTyped(e.target.value)} autoComplete="off" spellCheck={false} data-testid="confirm-input" />
          </label>
          {error && <p className="text-[13px] text-signal-soft">{error}</p>}
          <div className="flex flex-wrap justify-end gap-2 pt-1">
            <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
            <button
              type="submit"
              disabled={!ok || busy}
              className="inline-flex items-center justify-center border border-signal bg-signal px-4 py-2 font-mono text-[13px] font-semibold uppercase tracking-wider text-ink-950 transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-35"
              data-testid="confirm-go"
            >
              {busy ? "Working…" : action}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
