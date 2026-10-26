"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/practice", label: "Practice" },
  { href: "/review", label: "Review mistakes" },
  { href: "/quiz", label: "Timed quiz" },
];

/** Tabs that join open practice, mistake review and timed quizzes. */
export function PracticeTabs({ reviewCount }: { reviewCount?: number }) {
  const pathname = usePathname();
  return (
    <nav aria-label="Practice sections" className="flex gap-1 overflow-x-auto border-b border-ink-700" data-testid="practice-tabs">
      {TABS.map((t) => {
        const active = pathname === t.href || pathname.startsWith(`${t.href}/`);
        return (
          <Link
            key={t.href}
            href={t.href}
            aria-current={active ? "page" : undefined}
            className={`-mb-px flex items-center gap-2 whitespace-nowrap border-b-2 px-3 py-2 font-mono text-[12px] uppercase tracking-wider transition-colors max-sm:px-2 ${active ? "border-accent text-accent" : "border-transparent text-ink-300 hover:text-ink-50"}`}
          >
            {t.label}
            {t.href === "/review" && !!reviewCount && (
              <span className={`min-w-[1.5rem] border px-1 text-center text-[10px] leading-4 ${active ? "border-accent" : "border-ink-600 text-ink-200"}`}>{reviewCount}</span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
