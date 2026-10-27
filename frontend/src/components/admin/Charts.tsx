/** Small hand-drawn charts for the admin console: plain HTML/CSS, no chart library. */
import { niceMax, num, pct } from "@/lib/adminFormat";
import type { Bar, Overview } from "@/lib/adminApi";

export function ActivityChart({ days }: { days: Overview["daily"] }) {
  const max = niceMax(days.map((d) => d.answers + d.runs));
  const total = days.reduce((s, d) => s + d.answers + d.runs, 0);
  return (
    <figure className="space-y-3" data-testid="activity-chart">
      <figcaption className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="label">Daily activity · last {days.length} days</span>
        <span className="flex gap-4 font-mono text-[11px] text-ink-400">
          <span className="flex items-center gap-1.5"><i className="inline-block h-2 w-2 bg-accent" /> Answers</span>
          <span className="flex items-center gap-1.5"><i className="inline-block h-2 w-2 bg-ink-400" /> Code runs</span>
        </span>
      </figcaption>
      <div className="relative">
        <div className="pointer-events-none absolute inset-0 flex flex-col justify-between" aria-hidden="true">
          {[max, max / 2, 0].map((v) => (
            <div key={v} className="flex items-center gap-2">
              <span className="w-7 shrink-0 text-right font-mono text-[10px] text-ink-600">{v}</span>
              <span className="h-px flex-1 bg-ink-800" />
            </div>
          ))}
        </div>
        <div className="relative ml-9 flex h-44 items-end gap-[2px] sm:gap-1" role="img" aria-label={`${total} answers and code runs over ${days.length} days`}>
          {days.map((d) => {
            const a = (d.answers / max) * 100;
            const r = (d.runs / max) * 100;
            return (
              <div key={d.date} className="group relative flex h-full flex-1 flex-col justify-end" title={`${d.date}: ${d.answers} answers, ${d.runs} runs, ${d.learners} learners`}>
                <div className="bg-ink-400 transition-opacity group-hover:opacity-80" style={{ height: `${r}%` }} />
                <div className="bg-accent transition-opacity group-hover:opacity-80" style={{ height: `${a}%` }} />
              </div>
            );
          })}
        </div>
      </div>
      <div className="ml-9 flex justify-between font-mono text-[10px] text-ink-500">
        {days.filter((_, i) => i % 7 === 0 || i === days.length - 1).map((d) => (
          <span key={d.date}>{new Date(`${d.date}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
        ))}
      </div>
    </figure>
  );
}

export function BarList({ title, bars, empty, testid }: { title: string; bars: Bar[]; empty: string; testid?: string }) {
  const max = niceMax(bars.map((b) => b.attempts));
  return (
    <figure className="space-y-3" data-testid={testid}>
      <figcaption className="flex items-baseline justify-between gap-2">
        <span className="label">{title}</span>
        <span className="font-mono text-[10px] uppercase tracking-wider text-ink-500">attempts · right</span>
      </figcaption>
      {bars.length === 0 ? (
        <p className="text-[14px] text-ink-400">{empty}</p>
      ) : (
        <ul className="space-y-2">
          {bars.map((b) => (
            <li key={b.key} className="grid grid-cols-[minmax(0,8.5rem)_minmax(0,1fr)_auto] lg:grid-cols-[minmax(0,11rem)_minmax(0,1fr)_auto] items-center gap-3 text-[13px]">
              <span className="truncate text-ink-200" title={b.label}>{b.label}</span>
              <span className="relative h-3 border border-ink-800 bg-ink-950">
                <span className="absolute inset-y-0 left-0 bg-ink-600" style={{ width: `${(b.attempts / max) * 100}%` }} />
                <span className="absolute inset-y-0 left-0 bg-accent" style={{ width: `${(b.attempts / max) * 100 * (b.accuracy ?? 0)}%` }} />
              </span>
              <span className="w-[5.5rem] text-right font-mono text-[12px] tabular-nums text-ink-300">
                {num(b.attempts)} <span className="text-ink-500">· {pct(b.accuracy)}</span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </figure>
  );
}

/** A thin rate bar: lime for pass rates, signal for fail rates. */
export function RateBar({ value, tone = "pass" }: { value: number | null | undefined; tone?: "pass" | "fail" }) {
  return (
    <span className="flex items-center gap-2">
      <span className="relative h-1.5 w-14 shrink-0 bg-ink-800">
        <span className={`absolute inset-y-0 left-0 ${tone === "fail" ? "bg-signal" : "bg-accent"}`} style={{ width: `${(value ?? 0) * 100}%` }} />
      </span>
      <span className={`font-mono text-[12px] tabular-nums ${tone === "fail" && (value ?? 0) >= 0.5 ? "text-signal-soft" : "text-ink-200"}`}>{pct(value)}</span>
    </span>
  );
}
