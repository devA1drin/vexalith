"use client";

import type { DomainProgress } from "@/lib/api";
import { CountUp } from "@/components/CountUp";

/** Mastery per skill: a 0–100 bar (25% blueprint grid) plus the number of attempts. */
export function MasteryChart({ domains }: { domains: DomainProgress[] }) {
  return (
    <div className="card p-6" data-testid="mastery-chart">
      <div className="mb-4 flex items-center justify-between">
        <span className="label">Mastery by skill</span>
        <span className="label">0 — 100 · attempts</span>
      </div>
      <div className="space-y-4">
        {domains.map((d, i) => {
          const pct = Math.round(d.mastery * 100);
          return (
            <div key={d.domain_slug} className="grid grid-cols-[minmax(0,9rem)_1fr_3rem_2rem] items-center gap-3 sm:grid-cols-[13rem_1fr_3rem_2.5rem]">
              <span className="truncate text-sm text-ink-200">{d.domain_name}</span>
              <div className="relative h-5 border border-ink-700 bg-ink-950" role="meter" aria-label={d.domain_name} aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
                {[25, 50, 75].map((g) => <span key={g} className="absolute inset-y-0 w-px bg-ink-800" style={{ left: `${g}%` }} />)}
                <div className="bar-grow absolute inset-y-0 left-0 bg-accent" style={{ width: `${pct}%`, ["--rd" as string]: `${i * 110}ms` }} />
              </div>
              <span className="text-right font-mono text-sm text-ink-50"><CountUp to={pct} delay={i * 110} /></span>
              <span className="text-right font-mono text-[12px] text-ink-400" title="attempts">{d.attempts}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
