"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { adminApi, type Overview } from "@/lib/adminApi";
import { num, pct } from "@/lib/adminFormat";
import { AdminHeading, Notice } from "@/components/admin/AdminShell";
import { ActivityChart, BarList, RateBar } from "@/components/admin/Charts";

export default function AdminOverview() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    adminApi.overview().then(setData).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load the overview."));
  }, []);

  if (error) return <Notice tone="error">{error}</Notice>;
  if (!data) return <p className="font-mono text-[12px] text-ink-500">Loading…</p>;
  const t = data.totals;
  const cells: [string, string, string][] = [
    ["Learners", num(t.learners), `${num(t.new_7d)} new this week`],
    ["Active · 7 days", num(t.active_7d), `${pct(t.learners ? t.active_7d / t.learners : null)} of learners`],
    ["Active · 30 days", num(t.active_30d), `${pct(t.learners ? t.active_30d / t.learners : null)} of learners`],
    ["Answers", num(t.attempts), `${num(t.attempts_7d)} this week`],
    ["Accuracy", pct(t.accuracy), `${pct(t.partial_rate)} partly right`],
    ["Code runs", num(t.exercise_runs), `${pct(t.exercise_solve_rate)} pass every test`],
  ];

  return (
    <div className="space-y-8" data-testid="admin-overview">
      <AdminHeading kicker="Overview" title="How learners are doing">
        Live numbers from the database. Answers are graded explanations and fill-ins; code runs are exercise submissions.
      </AdminHeading>

      <dl className="grid grid-cols-2 border-l border-t border-ink-700 md:grid-cols-3 xl:grid-cols-6" data-testid="admin-totals">
        {cells.map(([k, v, s]) => (
          <div key={k} className="min-w-0 border-b border-r border-ink-700 bg-ink-900 px-4 py-4">
            <dt className="label truncate">{k}</dt>
            <dd className="mt-2 font-display text-3xl leading-none tabular-nums text-ink-50">{v}</dd>
            <dd className="mt-2 truncate font-mono text-[11px] text-ink-500">{s}</dd>
          </div>
        ))}
      </dl>

      {t.feedback_unreviewed > 0 && (
        <Link href="/admin/feedback?status=new" className="flex flex-wrap items-center justify-between gap-2 border border-ink-700 bg-ink-900 px-4 py-3 text-[14px] text-ink-200 hover:border-accent">
          <span><span className="font-mono text-accent">{t.feedback_unreviewed}</span> feedback {t.feedback_unreviewed === 1 ? "entry" : "entries"} not reviewed yet</span>
          <span className="font-mono text-[12px] uppercase tracking-wider text-ink-400">Review →</span>
        </Link>
      )}

      <section className="card p-4 sm:p-5"><ActivityChart days={data.daily} /></section>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="card p-4 sm:p-5">
          <BarList title="Answers by topic" bars={data.by_topic} empty="No answers yet." testid="topic-chart" />
        </section>
        <section className="card space-y-6 p-4 sm:p-5">
          <BarList title="Answers by language" bars={data.by_language} empty="No answers yet." testid="language-chart" />
          <BarList title="Code runs by exercise topic" bars={data.exercises_by_topic} empty="No code runs yet." />
        </section>
      </div>

      <section className="card" data-testid="hardest">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-ink-700 px-4 py-3 sm:px-5">
          <h2 className="font-display text-xl text-ink-50">Hardest questions</h2>
          <span className="font-mono text-[11px] text-ink-500">by share of wrong answers · at least {data.hardest_min_attempts} attempts</span>
        </div>
        {data.hardest.length === 0 ? (
          <p className="px-5 py-6 text-[14px] text-ink-400">Not enough answers yet to call any question hard.</p>
        ) : (
          <ol>
            {data.hardest.map((q, i) => (
              <li key={q.id} className="grid grid-cols-[2rem_minmax(0,1fr)] items-center gap-x-3 gap-y-2 border-b border-ink-800 px-4 py-3 last:border-0 sm:grid-cols-[2rem_minmax(0,1fr)_6rem_8rem_5rem] sm:px-5">
                <span className="font-mono text-[12px] text-ink-500">{String(i + 1).padStart(2, "0")}</span>
                <span className="min-w-0">
                  <Link href={`/admin/questions/${q.id}`} className="block truncate text-[14px] text-ink-50 hover:text-accent">{q.title}</Link>
                  <span className="block truncate font-mono text-[11px] text-ink-500">{q.topic} · {q.language}</span>
                </span>
                <span className="col-start-2 flex items-center gap-4 sm:contents">
                  <span className="shrink-0 font-mono text-[12px] text-ink-400">{q.attempts} attempts</span>
                  <span className="min-w-0 flex-1"><RateBar value={q.fail_rate} tone="fail" /></span>
                  <span className="shrink-0 font-mono text-[12px] text-ink-300 sm:text-right" title="Elo-style rating, 0–1000; higher is harder">◆ {q.rating}</span>
                </span>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
