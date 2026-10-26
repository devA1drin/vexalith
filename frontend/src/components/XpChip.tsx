"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { LevelInfo, XpSyncOut } from "@/lib/api";
import { announceXp, XP_EVENT } from "@/lib/xp";
import { LevelMark } from "@/components/BadgeMark";

/** Level and XP in the header. Counting on load also brings any toast the learner hasn't seen. */
export function XpChip() {
  const [info, setInfo] = useState<LevelInfo | null>(null);

  useEffect(() => {
    const on = (e: Event) => setInfo((e as CustomEvent<XpSyncOut>).detail);
    window.addEventListener(XP_EVENT, on);
    announceXp();
    return () => window.removeEventListener(XP_EVENT, on);
  }, []);

  if (!info) return <span className="h-7 w-[4.5rem]" aria-hidden />;
  return (
    <Link
      href="/badges"
      className="group flex items-center gap-2 border border-ink-700 py-1 pl-1 pr-2.5 transition-colors hover:border-accent"
      data-testid="xp-chip"
      aria-label={`Level ${info.level}, ${info.level_name}. ${info.xp} XP, ${info.to_next} to the next level.`}
    >
      <LevelMark level={info.level} size={22} />
      <span className="flex flex-col leading-none">
        <span className="font-mono text-[11px] text-ink-100 group-hover:text-accent">{info.xp.toLocaleString()} XP</span>
        <span className="mt-1 block h-[3px] w-14 bg-ink-700">
          <span className="block h-full bg-accent" style={{ width: `${Math.max(4, info.progress * 100)}%` }} />
        </span>
      </span>
    </Link>
  );
}
