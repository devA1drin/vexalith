"use client";

import type { DomainProgress } from "@/lib/api";
import { CountUp } from "@/components/CountUp";

/** Horizontal mastery bars on a 0–100 scale with a 25% blueprint grid; bars grow in sequence. */
export function MasteryChart({ domains }: { domains: DomainProgress[] }) {
  return (
    <div className="card p-6" data-testid="mastery-chart">
      <div className="mb-4 flex items-center justify-between">
        <span className="label">Mastery by skill</span>
        <span className="label">0 — 100</span>
      </div>
      <div className="space-y-4">
        {domains.map((d, i) => {
          const pct = Math.round(d.mastery * 100);
          return (
            <div key={d.domain_slug} className="grid grid-cols-[minmax(0,9rem)_1fr_3rem] items-center gap-3 sm:grid-cols-[13rem_1fr_3rem]">
              <span className="truncate text-sm text-ink-200">{d.domain_name}</span>
              <div className="relative h-5 border border-ink-700 bg-ink-950" role="meter" aria-label={d.domain_name} aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
                {[25, 50, 75].map((g) => <span key={g} className="absolute inset-y-0 w-px bg-ink-800" style={{ left: `${g}%` }} />)}
                <div className="bar-grow absolute inset-y-0 left-0 bg-accent" style={{ width: `${pct}%`, ["--rd" as string]: `${i * 110}ms` }} />
              </div>
              <span className="text-right font-mono text-sm text-ink-50"><CountUp to={pct} delay={i * 110} /></span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
