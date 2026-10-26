"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/progress", label: "Progress" },
  { href: "/badges", label: "Level & badges" },
  { href: "/leaderboard", label: "Leaderboard" },
];

/** Tabs that join Progress, Level & badges and the Leaderboard. */
export function RanksTabs() {
  const pathname = usePathname();
  return (
    <nav aria-label="Progress sections" className="flex gap-1 overflow-x-auto border-b border-ink-700">
      {TABS.map((t) => {
        const active = pathname === t.href;
        return (
          <Link
            key={t.href}
            href={t.href}
            aria-current={active ? "page" : undefined}
            className={`-mb-px whitespace-nowrap border-b-2 px-3 py-2 font-mono text-[12px] uppercase tracking-wider transition-colors ${active ? "border-accent text-accent" : "border-transparent text-ink-300 hover:text-ink-50"}`}
          >
            {t.label}
          </Link>
        );
      })}
    </nav>
  );
}
