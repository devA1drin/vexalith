"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type FundamentalsStatus, type LanguageProgress, type ProgressOut } from "@/lib/api";
import { MasteryChart } from "@/components/MasteryChart";
import { CountUp } from "@/components/CountUp";
import { Recommendations } from "@/components/Recommendations";

export default function ProgressPage() {
  const [data, setData] = useState<ProgressOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.progress().then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/progress";
      else setError(e instanceof Error ? e.message : "Failed");
    });
  }, []);

  const weakest = data?.domains.length ? [...data.domains].sort((a, b) => a.mastery - b.mastery)[0] : null;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">03 · Progress{data && ` · ${data.display_name}`}</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Where your logic holds.</h1>
        </div>
        <Link href="/practice" className="btn-primary">Continue <span className="btn-arrow">→</span></Link>
      </div>
      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-48 animate-pulse" />}
      {data && (
        <>
          <div className="grid grid-cols-2 border-l border-t border-ink-700 sm:grid-cols-4">
            <Stat label="Answers" value={data.total_responses} i={0} />
            <Stat label="Skips" value={data.total_skips} i={1} />
            <Stat label="Avg mastery" value={Math.round(data.average_mastery * 100)} suffix="%" i={2} />
            <div className="rise border-b border-r border-ink-700 p-5" style={{ ["--rd" as string]: "240ms" }}>
              <div className="label">Focus next</div>
              <div className="mt-2 truncate font-display text-lg font-semibold text-accent">{weakest?.domain_name ?? "—"}</div>
            </div>
          </div>
          {data.fundamentals && <FundamentalsPanel s={data.fundamentals} />}
          <Recommendations />
          <MasteryChart domains={data.domains} />
          <div className="card overflow-x-auto">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">Mastery and attempts per skill</caption>
              <thead>
                <tr className="border-b border-ink-700">
                  <th className="label px-5 py-3 font-normal">Skill</th>
                  <th className="label px-5 py-3 text-right font-normal">Mastery</th>
                  <th className="label px-5 py-3 text-right font-normal">Attempts</th>
                </tr>
              </thead>
              <tbody>
                {data.domains.map((d) => (
                  <tr key={d.domain_slug} className="border-b border-ink-800 last:border-0">
                    <td className="px-5 py-3 text-ink-100">{d.domain_name}</td>
                    <td className="px-5 py-3 text-right font-mono text-ink-50">{Math.round(d.mastery * 100)}</td>
                    <td className="px-5 py-3 text-right font-mono text-ink-300">{d.attempts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <LanguageBreakdown rows={data.languages ?? []} />
        </>
      )}
    </div>
  );
}

function Stat({ label, value, suffix = "", i }: { label: string; value: number; suffix?: string; i: number }) {
  return (
    <div className="rise border-b border-r border-ink-700 p-5" style={{ ["--rd" as string]: `${i * 80}ms` }}>
      <div className="label">{label}</div>
      <div className="mt-2 font-display text-4xl font-bold text-ink-50"><CountUp to={value} delay={i * 80} />{suffix}</div>
    </div>
  );
}

const LANG_LABEL: Record<string, string> = {
  python: "Python", javascript: "JavaScript", php: "PHP", cpp: "C++", html: "HTML", css: "CSS", general: "General",
};

function LanguageBreakdown({ rows }: { rows: LanguageProgress[] }) {
  return (
    <section aria-labelledby="by-lang" className="card">
      <div className="flex items-baseline justify-between border-b border-ink-700 px-5 py-3">
        <h2 id="by-lang" className="label">By language</h2>
        <span className="label text-ink-500">answers · avg score</span>
      </div>
      {rows.length === 0 ? (
        <p className="px-5 py-4 text-sm text-ink-400">Answer a question to see your per-language scores.</p>
      ) : (
        <ul>
          {rows.map((r) => {
            const pct = Math.round(r.average_score * 100);
            return (
              <li key={r.language} className="grid grid-cols-[6.5rem_1fr_auto] items-center gap-4 border-b border-ink-800 px-5 py-3 last:border-0" data-lang-row={r.language}>
                <span className="font-mono text-[12px] uppercase tracking-wider text-ink-100">{LANG_LABEL[r.language] ?? r.language}</span>
                <span className="h-1.5 bg-ink-800" aria-hidden="true">
                  <span className="bar-grow block h-full bg-accent" style={{ width: `${pct}%` }} />
                </span>
                <span className="font-mono text-sm text-ink-300">
                  {r.attempts} · <span className="text-ink-50">{pct}%</span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

function FundamentalsPanel({ s }: { s: FundamentalsStatus }) {
  const done = Math.min(s.answers, s.min_answers);
  const avg = Math.round(s.recent_average * 100);
  const need = Math.round(s.pass_average * 100);
  const state = s.cleared ? "cleared" : s.experienced ? "optional" : "in progress";
  return (
    <section aria-labelledby="fund-h" className="card grid gap-5 p-5 sm:grid-cols-[1fr_auto] sm:items-center" data-testid="fundamentals-panel">
      <div>
        <div className="flex items-baseline gap-3">
          <h2 id="fund-h" className="label">00 · Fundamentals</h2>
          <span className={`font-mono text-[11px] uppercase tracking-wider ${s.cleared ? "text-accent" : "text-ink-400"}`}>{state}</span>
        </div>
        <p className="mt-2 text-sm text-ink-300">
          {s.cleared
            ? "Basics cleared: practice now covers every skill and returns to Fundamentals if they slip."
            : s.experienced
              ? "You already practise other skills. Turn on Focus: Fundamentals on the practice page to drill the basics."
              : `Answer ${s.min_answers} Fundamentals questions averaging ${need}% or more to unlock every skill.`}
        </p>
      </div>
      <div className="flex items-center gap-4 font-mono text-sm">
        <div className="flex gap-1" role="img" aria-label={`${done} of ${s.min_answers} answers`}>
          {Array.from({ length: s.min_answers }, (_, i) => (
            <span key={i} className={`h-3 w-5 border ${i < done ? "border-accent bg-accent" : "border-ink-600"}`} />
          ))}
        </div>
        <span className="text-ink-300">
          avg <span className={avg >= need ? "text-accent" : "text-ink-50"}>{s.answers ? `${avg}%` : "—"}</span>
          <span className="text-ink-500"> / {need}%</span>
        </span>
      </div>
    </section>
  );
}
