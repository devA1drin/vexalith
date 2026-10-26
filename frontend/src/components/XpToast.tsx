"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { XpSyncOut } from "@/lib/api";
import { XP_EVENT } from "@/lib/xp";
import { BadgeMark, LevelMark } from "@/components/BadgeMark";

type Toast = { id: number; kind: "xp" | "badge" | "level"; title: string; body: string; badge?: string; group?: string; level?: number };

const SHOW_MS = 6500;

/** Toasts for XP gained, badges earned and level-ups. Mounted once in the layout. */
export function XpToaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const lastLevel = useRef<number | null>(null);
  const seq = useRef(0);

  const dismiss = useCallback((id: number) => setToasts((t) => t.filter((x) => x.id !== id)), []);

  useEffect(() => {
    const on = (e: Event) => {
      const out = (e as CustomEvent<XpSyncOut>).detail;
      const n = out.news;
      const next: Toast[] = [];
      const add = (t: Omit<Toast, "id">) => next.push({ ...t, id: ++seq.current });
      if (n.retro && (n.xp > 0 || n.badges.length)) {
        const b = n.badges.length;
        add({
          kind: "xp",
          title: "Your past work counts",
          body: `+${n.xp.toLocaleString()} XP${b ? ` and ${b} badge${b === 1 ? "" : "s"}` : ""} for what you've already done.`,
        });
      } else {
        if (n.xp > 0) {
          const one = n.items.length === 1 ? n.items[0].label : `${n.items.length} awards`;
          add({ kind: "xp", title: `+${n.xp} XP`, body: one });
        }
        for (const b of n.badges.slice(0, 3)) add({ kind: "badge", title: `Badge earned: ${b.name}`, body: b.description, badge: b.key });
      }
      if (lastLevel.current !== null && out.level > lastLevel.current) {
        add({ kind: "level", title: `Level ${out.level}: ${out.level_name}`, body: `${out.to_next.toLocaleString()} XP to ${out.next_level_name}.`, level: out.level });
      }
      lastLevel.current = out.level;
      if (!next.length) return;
      setToasts((t) => [...t, ...next].slice(-4));
      for (const t of next) window.setTimeout(() => dismiss(t.id), SHOW_MS);
    };
    window.addEventListener(XP_EVENT, on);
    return () => window.removeEventListener(XP_EVENT, on);
  }, [dismiss]);

  return (
    <div aria-live="polite" className="pointer-events-none fixed inset-x-3 bottom-3 z-50 flex flex-col items-end gap-2 sm:inset-x-auto sm:right-5 sm:bottom-5">
      {toasts.map((t) => (
        <div
          key={t.id}
          role="status"
          data-testid={`toast-${t.kind}`}
          className="rise pointer-events-auto flex w-full items-start gap-3 border border-ink-600 border-l-2 border-l-accent bg-ink-900 p-3 shadow-[0_12px_40px_rgba(0,0,0,0.5)] sm:w-[22rem]"
        >
          <div className="shrink-0">
            {t.kind === "badge" && t.badge ? (
              <BadgeMark id={t.badge} group={groupOf(t.badge)} earned size={40} />
            ) : t.kind === "level" && t.level ? (
              <LevelMark level={t.level} size={40} />
            ) : (
              <span className="flex h-10 w-10 items-center justify-center border border-accent font-mono text-[11px] font-bold text-accent">XP</span>
            )}
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-display text-[15px] font-semibold text-ink-50">{t.title}</p>
            <p className="mt-0.5 text-[13px] leading-snug text-ink-300">{t.body}</p>
          </div>
          <button type="button" onClick={() => dismiss(t.id)} className="-mr-1 -mt-1 px-1.5 font-mono text-ink-400 hover:text-ink-50" aria-label="Dismiss">
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

function groupOf(key: string): "answers" | "streaks" | "languages" | "code" {
  if (key.startsWith("ex-") || key === "unassisted" || key === "polyglot") return "code";
  if (key.startsWith("streak") || key === "daily-first") return "streaks";
  if (["cpp-answer", "java-answer", "oop-answer", "filipino"].includes(key)) return "languages";
  return "answers";
}
