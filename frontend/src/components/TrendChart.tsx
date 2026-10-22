"use client";

import type { ProgressDay } from "@/lib/api";

const W = 720;
const H = 220;
const PAD = { l: 34, r: 12, t: 14, b: 26 };

function short(iso: string) {
  const [, m, d] = iso.split("-").map(Number);
  return `${d} ${["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1]}`;
}

/** 30-day trend: average score per active day (line) over the number of answers (bars). */
export function TrendChart({ days, improvement }: { days: ProgressDay[]; improvement: number | null | undefined }) {
  const iw = W - PAD.l - PAD.r;
  const ih = H - PAD.t - PAD.b;
  const step = iw / Math.max(days.length, 1);
  const maxAnswers = Math.max(1, ...days.map((d) => d.answers));
  const x = (i: number) => PAD.l + step * i + step / 2;
  const y = (v: number) => PAD.t + ih * (1 - v);
  const pts = days.map((d, i) => (d.average_score == null ? null : { x: x(i), y: y(d.average_score), d })).filter(Boolean) as {
    x: number; y: number; d: ProgressDay;
  }[];
  const path = pts.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
  const active = days.filter((d) => d.answers > 0).length;
  const imp = improvement == null ? null : Math.round(improvement * 100);

  return (
    <section className="card" aria-labelledby="trend-h" data-testid="trend-chart">
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-ink-700 px-5 py-3">
        <h2 id="trend-h" className="label">Score over the last 30 days</h2>
        <span className="flex items-center gap-4 font-mono text-[11px] uppercase tracking-wider text-ink-400">
          <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-4 bg-accent" />avg score</span>
          <span className="flex items-center gap-1.5"><span className="inline-block h-2.5 w-2 bg-ink-600" />answers</span>
        </span>
      </div>
      {active === 0 ? (
        <p className="px-5 py-8 text-sm text-ink-400">Answer a few questions and your trend line appears here.</p>
      ) : (
        <div className="grid gap-4 p-5 lg:grid-cols-[1fr_12rem]">
          <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" role="img" aria-label={`Average score on ${active} active days in the last 30 days`}>
            {[0, 0.5, 1].map((g) => (
              <g key={g}>
                <line x1={PAD.l} x2={W - PAD.r} y1={y(g)} y2={y(g)} className="stroke-ink-800" strokeDasharray={g === 0 ? undefined : "2 4"} />
                <text x={PAD.l - 8} y={y(g) + 4} textAnchor="end" className="fill-ink-500 font-mono text-[10px]">{g * 100}</text>
              </g>
            ))}
            {days.map((d, i) =>
              d.answers ? (
                <rect key={d.date} x={x(i) - step * 0.3} width={step * 0.6} y={PAD.t + ih - (ih * 0.45 * d.answers) / maxAnswers} height={(ih * 0.45 * d.answers) / maxAnswers} className="fill-ink-700">
                  <title>{`${short(d.date)}: ${d.answers} answers, ${d.correct} correct`}</title>
                </rect>
              ) : null,
            )}
            {pts.length > 1 && <path d={path} fill="none" className="stroke-accent" strokeWidth={2} strokeLinejoin="round" />}
            {pts.map((p) => (
              <circle key={p.d.date} cx={p.x} cy={p.y} r={3.5} className="fill-ink-950 stroke-accent" strokeWidth={2}>
                <title>{`${short(p.d.date)}: avg ${Math.round((p.d.average_score ?? 0) * 100)} over ${p.d.answers} answers`}</title>
              </circle>
            ))}
            {days.map((d, i) =>
              i % 7 === 2 || i === days.length - 1 ? (
                <text key={d.date} x={x(i)} y={H - 6} textAnchor="middle" className="fill-ink-500 font-mono text-[10px]">
                  {i === days.length - 1 ? "today" : short(d.date)}
                </text>
              ) : null,
            )}
          </svg>
          <dl className="grid self-start gap-px border border-ink-700 bg-ink-700 text-sm">
            <div className="bg-ink-950 p-3">
              <dt className="label">Improvement</dt>
              <dd className={`mt-1 font-display text-2xl font-bold ${imp == null ? "text-ink-400" : imp >= 0 ? "text-accent" : "text-signal-soft"}`} data-testid="improvement">
                {imp == null ? "—" : `${imp > 0 ? "+" : ""}${imp} pts`}
              </dd>
              <dd className="mt-1 text-[12px] text-ink-500">recent answers vs the ones before</dd>
            </div>
            <div className="bg-ink-950 p-3">
              <dt className="label">Active days</dt>
              <dd className="mt-1 font-display text-2xl font-bold text-ink-50">{active}<span className="text-sm font-normal text-ink-500"> / 30</span></dd>
            </div>
          </dl>
        </div>
      )}
    </section>
  );
}
