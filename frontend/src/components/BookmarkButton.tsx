"use client";

import { useBookmark } from "@/lib/bookmarkStore";

/** Save / unsave a question ("q:<id>") or coding exercise ("x:<slug>"). */
export function BookmarkButton({ itemKey, compact = false, className = "" }: { itemKey: string; compact?: boolean; className?: string }) {
  const { saved, busy, error, toggle } = useBookmark(itemKey);
  const label = saved ? "Saved" : "Save";
  return (
    <button
      type="button"
      onClick={toggle}
      disabled={saved === null || busy}
      aria-pressed={!!saved}
      aria-label={saved ? "Remove from bookmarks" : "Save to bookmarks"}
      title={error ?? (saved ? "Saved to your bookmarks. Click to remove." : "Save to your bookmarks")}
      className={`inline-flex shrink-0 items-center gap-1.5 border px-2 py-1 font-mono text-[11px] uppercase tracking-wider transition-colors disabled:opacity-50 ${
        saved ? "border-accent text-accent" : "border-ink-700 text-ink-300 hover:border-ink-400 hover:text-ink-50"
      } ${error ? "border-signal" : ""} ${className}`}
      data-testid="bookmark"
      data-saved={saved ? "1" : "0"}
    >
      <svg viewBox="0 0 12 14" width="10" height="12" aria-hidden="true">
        <path d="M1 1h10v12L6 9.5 1 13z" fill={saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5" strokeLinejoin="miter" />
      </svg>
      {!compact && <span>{label}</span>}
    </button>
  );
}
